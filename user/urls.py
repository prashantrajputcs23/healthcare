from django.urls import path
from .views import *

app_name = 'user'

urlpatterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
    path('list', UserListView.as_view(), name='users'),
    path('add', UserCreateView.as_view(), name='add_user'),
    path('update/<pk>', UserUpdateView.as_view(), name='update_user'),
    path('staff_attendance_report', staff_attendance_report, name='staff_attendance_report'),
    path('attendance/mark_out', mark_out, name='attendance_mark_out'),
    path('ip/add/whitelist', add_to_whitelist, name='add_to_whitelist'),
]
