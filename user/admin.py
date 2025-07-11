from django.contrib import admin

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import UserAdmin

from user.forms import CustomUserCreationForm, CustomUserChangeForm
from user.models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("first_name", "last_name", "email","phone", "gender", "is_staff", "is_active", 'is_superuser', 'site')
    search_fields = ("email", 'first_name', 'last_name', "phone")
    ordering = ("email",)
    list_filter = ["gender", "is_active", 'site']
    fieldsets = (
        (None, {"fields": ("first_name", "last_name","email","phone", "password", "gender")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser" , "is_active",  "groups","user_permissions",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name", "last_name",
                "email","phone", "password1", "password2",
                "gender",
                "is_active", "is_staff", "is_superuser", "groups", "user_permissions",
            )},

         ),
    )


admin.site.register(User, CustomUserAdmin)


app_models = apps.get_app_config('user').get_models()
for model in app_models:
    try:
        @admin.register(model)
        class UserAdmin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
    except AlreadyRegistered:
        pass
