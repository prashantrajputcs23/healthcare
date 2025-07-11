from datetime import datetime, date, timedelta

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, CreateView
from sweetify.views import SweetifySuccessMixin

from doctor.forms import AppointmentForm
from doctor.models import Doctor, Appointment, Availability
from event.models import Event
from healthcare.utils import logger
from patient.forms import PatientForm
from patient.models import Patient
from web.forms import MessageForm
from web.models import *


class HomePage(TemplateView):
    template_name = 'web/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slides = Slider.active_sliders()
        context.update({'slides': slides})
        about = About.active_abouts().filter(title=AboutHeadingChoice.about_clinic).first()
        why_to_choose_us = About.active_abouts().filter(title=AboutHeadingChoice.why_to_choose_us).first()
        context.update({'about': about, 'why_to_choose_us': why_to_choose_us})
        services = Services.active_services().order_by('?')
        # service_row_1 = services[:3]
        # service_row_1_ids = list(service_row_1.values_list('id', flat=True))
        # service_row_2 = services.exclude(id__in=service_row_1_ids)[:4]
        context.update({'services': services})
        offer = Offer.active_offers(self.request)
        if offer.exists():
            context.update({'offer': offer.first()})
        events = Event.upcoming_events()
        context.update({'events': events})
        testimonials = Testimonial.active_testimonials().order_by('?')[:6]
        context.update({'testimonials': testimonials})
        doctors = Doctor.active_doctors()[:9]
        context.update({'doctors': doctors})
        our_treatments = OurTreatment.all(request=self.request)
        context.update({'our_treatments': our_treatments})
        patient_form = PatientForm()
        appointment_form = AppointmentForm()
        context.update({'patient_form': patient_form, 'appointment_form': appointment_form})
        return context


class AboutPage(TemplateView):
    template_name = 'web/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        abouts = About.active_abouts()
        context.update({'abouts': abouts})
        return context


class ServicePage(TemplateView):
    template_name = 'web/service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all active services
        services = Services.active_services()

        # Get department filter from request
        department = self.request.GET.get('department')

        # Filter services by department if department parameter is present
        if department:
            services = services.filter(department__name__iexact=department)

        # Add filtered or unfiltered services to the context
        context.update({'services': services})

        # Get all active doctors' department IDs and filter departments based on those IDs
        department_ids = Doctor.active_doctors().values_list('department_id', flat=True)
        departments = Department.departments().filter(id__in=department_ids)

        # Add departments to the context
        context.update({'departments': departments})

        return context


class ServiceDetailView(DetailView):
    model = Services
    template_name = 'web/service_details.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        # Get similar services from the same department
        similar_services = Services.active_services().filter(department=service.department).exclude(id=service.id)[:3]
        context['similar_services'] = similar_services
        return context


class ContactPage(SweetifySuccessMixin, CreateView):
    template_name = 'web/contact.html'
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('web:contact_page')
    success_message = 'Inquiry sent successfully.'
    error_message = 'There was an error with your submission. Please try again.'

    def form_valid(self, form):
        logger.debug("Form is valid and saving")  # Log or print to debug
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        logger.debug("Form is invalid: %s", form.errors)  # Log form errors
        return super().form_invalid(form)


def create_appointment(request):
    patient_form = PatientForm()
    appointment_form = AppointmentForm()

    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        appointment_form = AppointmentForm(request.POST)
        patient_data = patient_form.data
        patient = Patient.objects.filter(name__iexact=patient_data['name'], phone=patient_data['phone'])
        if patient.exists():
            patient = patient.first()
            if hasattr(patient_form, 'errors'):
                patient_form.errors.clear()
        else:
            if patient_form.is_valid():
                patient = patient_form.save()
            else:
                print(appointment_form.errors)
        if appointment_form.is_valid() and patient_form.is_valid():
            appointment = appointment_form.save(commit=False)
            appointment.patient = patient
            appointment.organisation = current_site().organization
            appointment.site = current_site()
            try:
                appointment_form.save()
                # Redirect or other logic after successful save
            except IntegrityError:
                # Add a non-field error for duplicate key violation
                appointment_form.add_error(None,"An appointment with this doctor, patient, location, and date already exists.")
                return render(request, 'web/appointment.html',
                              {'patient_form': patient_form, 'appointment_form': appointment_form})
            return redirect(reverse_lazy('web:home_page'))
        else:
            print(appointment_form.errors)
    return render(request, 'web/appointment.html',
                  {'patient_form': patient_form, 'appointment_form': appointment_form})


def load_doctor_branches(request):
    doctor_id = request.GET.get('doctor_id')
    branches = Branch.all_branches().filter(doctors=doctor_id)
    if branches.exists():
        branches_list = [{
            'id': branch.id,
            'address': str(branch.address)  # Convert address to string
        } for branch in branches]
        return JsonResponse({'success': True, 'branches': branches_list}, safe=False)
    else:
        return JsonResponse({'success': False, 'message': 'Doctor is not available'}, safe=False)


def load_available_date(request):
    doctor_id = request.GET.get('doctor_id')
    branch_id = request.GET.get('branch_id')
    today = timezone.now().date()
    dates = Availability.objects.filter(doctor_id=doctor_id, branch_id=branch_id, date__gte=today)
    if dates.exists():
        dates = list(dates.values_list('date', flat=True))
        return JsonResponse({'success': True, 'dates': dates}, safe=False)
    else:
        return JsonResponse({'success': False, 'message': 'Doctor is not available'}, safe=False)


def load_time_slot(request):
    doctor_id = request.GET.get('doctor_id')
    selected_date = request.GET.get('date')
    if doctor_id and selected_date:
        try:
            availability = Availability.objects.get(doctor_id=doctor_id, date=selected_date)
            doctor = Doctor.objects.get(id=doctor_id)

            # Generate time slots using the Doctor model's method
            all_slots = doctor.generate_time_slots(availability)

            # Fetch all appointments for the selected doctor on the same date
            booked_appointments = Appointment.objects.filter(
                doctor_id=doctor_id,
                date=selected_date
            ).values_list('start_time', 'end_time')

            # Convert appointment times to a list of start and end times
            booked_times = [(datetime.combine(date.min, appt_start), datetime.combine(date.min, appt_end))
                            for appt_start, appt_end in booked_appointments]

            # Filter out slots that conflict with existing appointments
            def is_slot_available(slot):
                slot_start = datetime.combine(date.min, slot)
                slot_end = slot_start + timedelta(seconds=int(doctor.slot_duration.total_seconds()))
                for appt_start, appt_end in booked_times:
                    if (appt_start < slot_end and slot_start < appt_end):
                        return False
                return True

            available_slots = [slot for slot in all_slots if is_slot_available(slot)]
            print(available_slots)
            return JsonResponse({'success': True, 'times': [slot.strftime("%H:%M") for slot in available_slots]})

        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Doctor is not available on this date'}, safe=False)

    return JsonResponse({'success': False, 'message': 'Invalid doctor or date'}, safe=False)
