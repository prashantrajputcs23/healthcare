from django.template.loader import render_to_string

from diagnostics.models import Vital, Diagnosis
from medications.models import Prescription, PrescriptionDetail
from patient.models import Patient
import calendar
import sweetify
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView

from doctor.models import Availability, Appointment, Doctor
from healthcare.utils import month_name_to_number, get_dates_in_month, current_site
from medications.forms import PrescriptionForm, PrescriptionDetailForm, DiagnosisForm, VitalForm


class RelatedObjectDoesNotExist:
    pass


@login_required(login_url=reverse_lazy('user:login'))
def create_update_availability(request):
    doctor_id = request.GET.get('doctor_id')
    doctor = None
    try:
        if doctor_id:
            doctor = get_object_or_404(Doctor, pk=doctor_id)
        else:
            doctor = request.user.doctor
    except Exception as e:
        sweetify.warning(request, 'Restricted', text='You are not a doctor', persistent=True)
        return redirect(reverse_lazy('user:dashboard'))
    if request.method == 'POST':
        same_for_all_days = request.POST.get('same_for_all_days') == 'on'
        month_year = request.POST.get('month_year').split()
        # Convert month name to number
        month_name = month_year[0]
        year = int(month_year[1])
        month = month_name_to_number(month_name)

        if month is None:
            return JsonResponse({'status': 'error', 'errors': [{'date': '', 'error': 'Invalid month name.'}]},
                                status=400)

        # Get dates in the selected month
        days = get_dates_in_month(year, month)
        errors = []
        valid_data = []

        for day in days:
            is_available = request.POST.get(f'available_{day}') == 'on'
            start_time = request.POST.get(f'start_time_{day}')
            end_time = request.POST.get(f'end_time_{day}')
            lunch_start_time = request.POST.get(f'lunch_start_time_{day}')
            lunch_end_time = request.POST.get(f'lunch_end_time_{day}')

            if is_available:
                # Validate start and end times
                try:
                    if start_time and end_time and start_time >= end_time:
                        raise ValidationError(f"End time must be after start time.")
                    if lunch_start_time and lunch_end_time and lunch_start_time >= lunch_end_time:
                        raise ValidationError(f"Lunch end time must be after lunch start time.")
                except ValidationError as e:
                    errors.append({'date': day.strftime('%Y-%m-%d'), 'error': str(e)})
                    # Skip this date's data and continue with the next date
                    continue

                # Add to valid data if no errors
                try:
                    doctor_id = request.POST.get('doctor_id')
                    if doctor_id:
                        doctor = get_object_or_404(Doctor, pk=doctor_id)
                    else:
                        doctor = request.user.doctor
                except Exception as e:
                    pass

                valid_data.append({
                    'doctor': doctor,
                    'date': day,
                    'start_time': start_time,
                    'end_time': end_time,
                    'lunch_start_time': lunch_start_time,
                    'lunch_end_time': lunch_end_time,
                    'is_available': is_available
                })
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        # Save valid data
        for data in valid_data:
            availability, created = Availability.objects.get_or_create(
                doctor=data['doctor'],
                date=data['date'],
                defaults={
                    'start_time': data['start_time'],
                    'end_time': data['end_time'],
                    'lunch_start_time': data['lunch_start_time'],
                    'lunch_end_time': data['lunch_end_time'],
                    'is_available': data['is_available'],
                    'organisation': current_site().organization,
                    'site': current_site(),
                    'branch_id': request.POST.get('branch')
                }
            )
            availability.start_time = data['start_time']
            availability.end_time = data['end_time']
            availability.lunch_start_time = data['lunch_start_time']
            availability.lunch_end_time = data['lunch_end_time']
            availability.is_available = data['is_available']
            availability.save()

        return JsonResponse({'status': 'success'}, status=200)
    return render(request, 'doctor/create_update_availability.html', {'doctor': doctor})


@login_required(login_url=reverse_lazy('user:login'))
def get_doctor_availability_for_month(request):
    if request.method == 'GET':
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        doctor_id = request.GET.get('doctor_id')
        print('doctor_id: ', doctor_id)
        doctor = request.user.doctor
        if doctor_id:
            doctor = get_object_or_404(Doctor, pk=doctor_id)
        days_in_month = get_dates_in_month(year, month)  # Assuming this returns a list of date objects for the month
        availability_data = []

        for day in days_in_month:
            day_of_week = calendar.day_name[day.weekday()]  # Get the day of the week (e.g., 'Monday', 'Tuesday')
            availability = Availability.objects.filter(doctor=doctor, date=day).first()
            availability_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_of_week': day_of_week,  # Add day of the week to the response
                'available': availability.is_available if availability else False,
                'start_time': availability.start_time.strftime(
                    '%H:%M') if availability and availability.start_time else '',
                'end_time': availability.end_time.strftime('%H:%M') if availability and availability.end_time else '',
                'lunch_start_time': availability.lunch_start_time.strftime(
                    '%H:%M') if availability and availability.lunch_start_time else '',
                'lunch_end_time': availability.lunch_end_time.strftime(
                    '%H:%M') if availability and availability.lunch_end_time else '',
            })

        return JsonResponse({'days': availability_data}, safe=False)


class AppointmentListView(ListView):
    model = Appointment
    queryset = Appointment.all()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied: Superusers only")  # ❌ Deny access

        return super().dispatch(request, *args, **kwargs)

def core_template(request):
    patient = Patient.objects.get(id='bb5bc46a-7ee2-40a6-913f-0c90af6a6d21')
    return render(request, 'medications/prescription_form.html', {'patient': patient})


def save_prescription_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            context = {}
            data['html_group_list'] = render_to_string('doctor/includes/_prescription_detail_list.html', context)
    else:
        data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    print(data)
    return JsonResponse(data)


def create_prescription(request):
    form = PrescriptionDetailForm()
    return save_prescription_form(request, form, 'doctor/includes/_prescription_detail_create.html')


def save_vital_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
    else:
        data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def save_diagnosis_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
    else:
        data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def create_vital(request):
    form = VitalForm()
    return save_vital_form(request, form, 'doctor/vital_create_form.html')


def create_diagnosis(request):
    form = DiagnosisForm()
    return save_diagnosis_form(request, form, 'doctor/vital_create_form.html')

