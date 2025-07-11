from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

app_models = apps.get_app_config('doctor').get_models()
for model in app_models:
    try:
        @admin.register(model)
        class UserAdmin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
    except AlreadyRegistered:
        pass