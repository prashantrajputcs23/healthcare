from django.contrib import admin
from .models import Patient
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    def delete_duplicates(self, request, queryset):
        # Call the class method to delete duplicates
        Patient.delete_duplicates()
        self.message_user(request, "Duplicates have been deleted.")

    delete_duplicates.short_description = "Delete duplicate records"

    resource_class = PatientResource
    list_display = ['name', 'age', 'gender', 'phone', 'address', 'created_at']
    list_filter = ['gender']
    search_fields = ['name', 'age', 'phone', 'address']
    actions = ['delete_duplicates']