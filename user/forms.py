import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render
from django.utils.timezone import now
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from doctor.models import Doctor
from user.models import User, Attendance


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone")


class CustomPhoneNumberPrefixWidget(PhoneNumberPrefixWidget):
    def subwidgets(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        return context['widget']['subwidgets']


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'gender']


class UserForm(forms.ModelForm):
    role = forms.CharField(max_length=100,
                           widget=forms.Select(choices=(('doctor', 'Doctor'), ('employee', 'employee'),)))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', "gender", 'email', 'phone', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
                Column('gender', css_class='col-md-6'),
                Column('role', css_class='col-md-6'),
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')

        if role:
            group, created = Group.objects.get_or_create(name=role)  # Get or create group
            user.save()  # Save user before adding to group (if not already saved)
            user.groups.add(group)  # Assign user to the group
        if commit:
            user.save()  # Save again after adding to group
        if role == 'doctor':
            doctor, _ = Doctor.objects.get_or_create(user=user)
        return user


class UserUpdateForm(forms.ModelForm):
    role = forms.CharField(max_length=100,
                           widget=forms.Select(choices=(('doctor', 'Doctor'), ('employee', 'Employee'),)))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', "gender", 'email', "phone", 'role', "is_active", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
                Column('gender', css_class='col-md-6'),
                Column('role', css_class='col-md-6'),
                Column('is_active', css_class='col-md-6'),
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role:
            group, created = Group.objects.get_or_create(name=role)
            user.save()
            user.groups.add(group)
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label="Email or Phone",
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=256,
    )
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Pop the 'request' argument to prevent errors
        super().__init__(*args, **kwargs)  # Call parent constructor

    def clean_username(self):
        username = self.cleaned_data.get("username").strip()

        # Validate Email
        try:
            validate_email(username)
            return username
        except ValidationError:
            pass

        # If it's a 10-digit phone number, add +91
        if re.match(r"^\d{10}$", username):
            return f"+91{username}"

        # If it's already in +91 format, return as is
        if re.match(r"^\+91\d{10}$", username):
            return username

        raise forms.ValidationError("Enter a valid Email, Phone Number.")

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid credentials. Please try again.")

            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        """Return the authenticated user"""
        return self.user_cache

def staff_attendance_dashboard(request):
    today = now()

    # Get all users in "Staff" group
    staff_group = Group.objects.get(name="Staff")
    staff_users = staff_group.user_set.all()

    # Fetch attendance for the current month
    attendance_data = Attendance.objects.filter(
        user__in=staff_users,
        creates_at__year=today.year,
        creates_at__month=today.month
    ).order_by('user', 'creates_at')

    # Create a dictionary { user: [attendance_list] }
    attendance_dict = {}
    for user in staff_users:
        attendance_dict[user] = attendance_data.filter(user=user)

    context = {
        'attendance_dict': attendance_dict,
    }
    return render(request, 'staff_attendance_dashboard.html', context)
