import json
from datetime import timedelta, date

from django.shortcuts import redirect
from django.utils.timezone import localtime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, F
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView
from django_filters.views import FilterView
from sweetify import sweetify

from healthcare.utils import get_page_context, HTMXCreateView, entry_per_page
from inventory.filters import SalesOrderFilter, PurchaseOrderFilter
from inventory.models import SalesOrder, PurchaseOrder, PharmacyProduct
from patient.filters import PatientFilter
from patient.models import Patient
from user.filters import UserFilter
from user.forms import *
from user.models import User, WhiteIP


class CustomLogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Clear all session data after logout
        for key in list(request.session.keys()):
            del request.session[key]
        return response

    def get_next_page(self):
        # Redirect to the configured logout URL
        return settings.LOGOUT_REDIRECT_URL


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        response = super().form_valid(form)

        if remember_me:
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            self.request.session.set_expiry(0)  # Session expires on browser close

        return response

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        return next_url if next_url else settings.LOGIN_REDIRECT_URL


@login_required(login_url=reverse_lazy('user:login'))
def dashboard(request):
    user = request.user
    patients = PatientFilter(request.GET, queryset=Patient.objects.all()).qs
    sales = SalesOrderFilter(request.GET, queryset=SalesOrder.all()).qs
    purchases = PurchaseOrderFilter(request.GET, queryset=PurchaseOrder.all()).qs

    # Filter sales and purchases based on user role
    if not user.is_superuser:
        sales = sales.filter(created_by=user)
        purchases = purchases.filter(created_by=user)

    total_sales = sales.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
    total_purchases = purchases.aggregate(total_purchases=Sum('total_amount'))['total_purchases'] or 0

    # Calculate credit_sales and cash_sales
    credit_sales_total = sales.filter(is_paid=False).aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0
    cash_sales_total = total_sales - credit_sales_total  # Calculate cash sales

    # Sales and Purchases data for chart
    sales_data_qs = (
        sales.values('created_at', 'created_by__first_name')
            .annotate(total_sales=Sum('total_amount'))
            .order_by('created_at')
    )
    sales_data = [
        {
            'created_at': record['created_at'].strftime('%Y-%m-%d'),
            'created_by__first_name': record['created_by__first_name'],
            'total_sales': float(record['total_sales']),
        }
        for record in sales_data_qs
    ]

    purchases_data_qs = (
        purchases.values('created_at', 'created_by__first_name')
            .annotate(total_purchases=Sum('total_amount'))
            .order_by('created_at')
    )
    purchases_data = [
        {
            'created_at': record['created_at'].strftime('%Y-%m-%d'),
            'created_by__first_name': record['created_by__first_name'],
            'total_purchases': float(record['total_purchases']),
        }
        for record in purchases_data_qs
    ]

    # Get pharmacy products with stock below reorder level
    low_stock_pharmacy_products = PharmacyProduct.objects.filter(quantity_in_stock__lt=F('reorder_level'))

    context = {
        'patients': patients,
        'cash_sales': cash_sales_total,
        'credit_sales': credit_sales_total,
        'total_sales': total_sales,  # Passing total sales value
        'total_purchases': total_purchases,
        'sales_data': json.dumps(sales_data, cls=DjangoJSONEncoder),
        'purchases_data': json.dumps(purchases_data, cls=DjangoJSONEncoder),
        'low_stock_pharmacy_products': low_stock_pharmacy_products,
        'period': request.GET.get('period', 'week'),
    }
    return render(request, 'user/index.html', context)

class UserListView(FilterView):
    model = User
    template_name = "user/user_list.html"
    context_object_name = "users"
    filterset_class = UserFilter
    paginate_by = entry_per_page

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied: Superusers only")  # ❌ Deny access

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.object_list
        context.update(get_page_context(self, queryset=filtered_queryset))
        return context

    def render_to_response(self, context, **response_kwargs):
        """Dynamically choose the HTMX or full template"""
        request = self.request

        # Check if request is from HTMX
        if request.htmx:
            print("htmx request on user list")
            response = render(request, 'user/partials/_users_list.html', context, **response_kwargs)
            response["HX-Retarget"] = "#table"  # ✅ Target table for update
            response["HX-Swap"] = "innerHTML"  # ✅ Swap content inside the table
            response["HX-Trigger"] = "refreshTable"  # ✅ Custom event for further actions
            return response

        # Serve normal template for non-HTMX requests
        return super().render_to_response(context, **response_kwargs)


class UserCreateView(HTMXCreateView):
    model = User
    form_class = UserForm
    template_name = "user/user_form.html"
    success_url = reverse_lazy("user:users")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied: Superusers only")  # ❌ Deny access

        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        """Handle form errors"""
        response = render(self.request, "user/user_form.html", {"form": form})

        response["HX-Retarget"] = ".form-container"
        response["HX-Swap"] = "innerHTML"
        response["HX-Trigger"] = "formError"

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('user:add_user')
        })
        return context


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "user/user_form.html"
    success_url = reverse_lazy("user:users")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied: Superusers only")  # ❌ Deny access

        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        """Handle form errors"""
        response = render(self.request, "user/user_form.html", {"form": form})
        response["HX-Retarget"] = ".form-container"
        response["HX-Swap"] = "innerHTML"
        response["HX-Trigger"] = "formError"
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('user:update_user', kwargs={'pk': self.object.pk})
        })
        return context


class UserDetailView(DetailView):
    model = User
    template_name = "user/user_detail.html"
    context_object_name = "user"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access Denied: Superusers only")  # ❌ Deny access

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.htmx:
            return render(request, "user/partials/_user_detail.html", {"user": self.object})
        return super().get(request, *args, **kwargs)


def staff_attendance_report(request):
    today = now().date()
    selected_month_str = request.GET.get('month', today.strftime('%Y-%m'))

    try:
        selected_year, selected_month = map(int, selected_month_str.split('-'))
    except ValueError:
        selected_year, selected_month = today.year, today.month

    first_day = date(selected_year, selected_month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    date_range = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    try:
        employee_group = Group.objects.get(name="employee")
        employee_users = employee_group.user_set.all()
        if not request.user.is_superuser:
            employee_users = employee_users.filter(pk=request.user.pk)
    except Group.DoesNotExist:
        employee_users = []

    attendance_records = Attendance.objects.filter(
        user__in=employee_users,
        in_time__date__range=(first_day, last_day)
    )

    # Fix status mapping
    status_map = {"Present": "P", "Absent": "A"}

    # Initialize attendance dictionary with proper structure
    attendance_dict = {
        user: {
            "dates": {date: "⏺" for date in date_range},
            "times": {},
            "present_count": 0
        }
        for user in employee_users
    }

    for record in attendance_records:
        status = status_map.get(record.get_status_display(), "⏺")
        record_date = record.in_time.date()

        in_time_str = localtime(record.in_time).strftime('%I:%M %p') if record.in_time else "-"
        out_time_str = localtime(record.out_time).strftime('%I:%M %p') if record.out_time else "-"

        # Store status and time
        attendance_dict[record.user]["dates"][record_date] = status
        attendance_dict[record.user]["times"][record_date] = {
            "in_time": in_time_str,
            "out_time": out_time_str,
        }

        # Fix counting logic
        if status == "P":
            attendance_dict[record.user]["present_count"] += 1  # Increment correctly

    context = {
        'attendance_dict': attendance_dict,
        'date_range': date_range,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    return render(request, 'user/staff_attendance_dashboard.html', context)


@login_required
def mark_out(request):
    user_ids = request.GET.getlist('user_ids')
    if not user_ids:
        user_ids = [request.user.pk]

    users = User.objects.filter(pk__in=user_ids)
    today = now().date()

    marked = []
    not_found = []

    for user in users:
        try:
            attendance = Attendance.objects.get(
                user=user,
                in_time__date=today,
                out_time__isnull=True
            )
            attendance.out_time = now()
            attendance.save()
            marked.append(user.username)
        except Attendance.DoesNotExist:
            not_found.append(user.username)

    return redirect(reverse_lazy('user:staff_attendance_report'))


def get_allowed_prefixes():
    # Fetch all saved IPs and extract their prefixes (like "127.0", "192.168")
    saved_ips = WhiteIP.objects.values_list('ip', flat=True)
    prefixes = set()

    for ip in saved_ips:
        parts = ip.split('.')
        if len(parts) >= 2:
            prefixes.add(f"{parts[0]}.{parts[1]}")
    return prefixes


def get_client_ip(request):
    # Handles X-Forwarded-For if behind a proxy/load balancer
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def add_to_whitelist(request):
    client_ip = get_client_ip(request)
    client_prefix = ".".join(client_ip.split('.')[:2])  # e.g. '103.25'

    white_ips = WhiteIP.objects.all()
    matched = False

    for white_ip in white_ips:
        white_ip_prefix = ".".join(white_ip.ip.split('.')[:2])
        if client_prefix == white_ip_prefix:
            # Match mil gaya – update karo
            white_ip.ip = client_ip
            white_ip.save()
            sweetify.success(request, f"IP {client_ip} matched and updated in whitelist.")
            matched = True
            break

    if not matched:
        sweetify.error(request, "Illegal IP Address detected.")
        return render(request, 'user/ip_blocked.html', {'message': 'Cannot add this IP address'})

    return redirect("user:staff_attendance_report")
