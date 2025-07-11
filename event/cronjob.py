# from datetime import timedelta
#
# from django.utils import timezone
#
# from event.models import EventMessageLog, Event
# from patient.models import Patient
# from healthcare.utils import WhatsappThread
#
#
def send_event_whatsapp(event_query_set, log_type):
    pass
#     log_type_to_attr = {
#         1: 'is_sent_1',
#         24: 'is_sent_24',
#         48: 'is_sent_48'
#     }
#
#     for event in event_query_set:
#         patients = Patient.objects.all()
#         for patient in patients:
#             WhatsappThread(event, patient).start()
#         event_reminder_email_log = event.event_message_log
#         log_attr = log_type_to_attr[log_type]
#         setattr(event_reminder_email_log, log_attr, True)
#         event_reminder_email_log.save()
#
#
# def event_cron_job():
#     now = timezone.now()
#     one_hour_later = now + timedelta(hours=0)
#     two_hours_later = now + timedelta(hours=2)
#
#     twenty_four_hours_later = now + timedelta(hours=23)
#     twenty_five_hours_later = now + timedelta(hours=25)
#
#     forty_eight_hours_later = now + timedelta(hours=48)
#     fifty_hours_later = now + timedelta(hours=50)
#
#     # Query for events within 0-2 hours
#     events_within_0_2_hours = Event.objects.filter(start__gte=one_hour_later, start__lte=two_hours_later)
#     print('events_within_0_2_hours', events_within_0_2_hours)
#     # Query for events within 23-25 hours
#     events_within_23_25_hours = Event.objects.filter(start__gte=twenty_four_hours_later,
#                                                      start__lte=twenty_five_hours_later)
#     print('events_within_23_25_hours', events_within_23_25_hours)
#     events_within_48_50_hours = Event.objects.filter(start__gte=forty_eight_hours_later,
#                                                      start__lte=fifty_hours_later)
#     print('events_within_48_50_hours', events_within_48_50_hours)
#     # Process reminders within 1-2 hours
#     send_event_whatsapp(events_within_0_2_hours, log_type=1)
#
#     # Process reminders within 24-25 hours
#     send_event_whatsapp(events_within_23_25_hours, log_type=24)
#
#     # Process reminders within 48-50 hours
#     send_event_whatsapp(events_within_48_50_hours, log_type=48)
#
#     event_email_logs = EventMessageLog.objects.filter(is_sent_1=True, is_sent_24=True)
#     event_email_logs.delete()