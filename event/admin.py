from django.contrib import admin
from .models import Event,EventMessageLog


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start', 'end', 'status', 'is_published', 'address', 'created_at']
    list_filter = ['status', 'is_published', 'start']
    search_fields = ['title']


@admin.register(EventMessageLog)
class EventMessageLogAdmin(admin.ModelAdmin):
    list_filter = ['event', 'is_sent_48', 'is_sent_24', 'is_sent_1']