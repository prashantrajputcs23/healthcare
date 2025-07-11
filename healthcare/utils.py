import calendar
import threading
import time
import uuid
from datetime import datetime, timedelta

import requests
import json
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import PageNotAnInteger
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)

from_whatsapp = 'whatsapp:+917983644202'
TWILIO_API_BASE_URL = "https://api.twilio.com/2010-04-01/Accounts"


class HTMXTemplateView(TemplateView):
    htmx_template_name = None

    def get_template_names(self):
        if self.request.htmx and self.htmx_template_name:
            print('htmx template')
            return [self.htmx_template_name]
        return [self.template_name]


class HTMXListView(ListView):
    htmx_template_name = None

    def get_template_names(self):
        if self.request.htmx and self.htmx_template_name:
            print('htmx template')
            return [self.htmx_template_name]
        return [self.template_name]


class HTMXCreateView(CreateView):
    htmx_template_name = None

    def get_template_names(self):
        if self.request.htmx and self.htmx_template_name:
            print('htmx Create View')
            return [self.htmx_template_name]
        return [self.template_name]


class HTMXUpdateView(UpdateView):
    htmx_template_name = None

    def get_template_names(self):
        if self.request.htmx and self.htmx_template_name:
            print('htmx template')
            return [self.htmx_template_name]
        return [self.template_name]


class HTMXDetailView(DetailView):
    htmx_template_name = None

    def get_template_names(self):
        if self.request.htmx and self.htmx_template_name:
            print('htmx template')
            return [self.htmx_template_name]
        return [self.template_name]


class WhatsappThread(threading.Thread):
    def __init__(self, event, patient, sleep=10):
        self.event = event
        self.patient = patient
        self.sleep = sleep
        self.template_sid = 'HX40c6a793cbd5adabd4afb7d5360121da'  # Your Template SID
        threading.Thread.__init__(self)

    def send_whatsapp_message(self, max_retries=5):
        url = f"{TWILIO_API_BASE_URL}/{settings.TWILIO_SID}/Messages.json"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Convert variables to a JSON string
        content_variables = json.dumps({
            '1': f'{self.event.start.date()}',
            '2': f'{self.event.get_day_of_event()}',
            '3': f'{self.event.start.time()}',
            '4': f'{self.event.end.time()}'
        })

        data = {
            'To': f'whatsapp:{self.patient.phone}',
            'From': from_whatsapp,
            'MessagingServiceSid': settings.TWILIO_MES_SID,
            'ContentSid': self.template_sid,  # Use your template SID
            'ContentVariables': content_variables  # Pass variables as JSON string
        }

        retry_count = 0
        backoff_time = 2  # Start with a 2-second delay

        while retry_count < max_retries:
            response = requests.post(
                url,
                data=data,
                auth=HTTPBasicAuth(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN),
                headers=headers
            )

            if response.status_code == 201:
                print("Message sent successfully")
                return True
            elif response.status_code == 429:  # Too Many Requests
                retry_count += 1
                print(f"Rate limit hit, retrying in {backoff_time} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(backoff_time)
                backoff_time *= 2  # Exponential backoff
            else:
                print(f"Failed to send message: {response.status_code}")
                print(response.text)
                return False

        print("Max retries reached, message not sent.")
        return False

    def run(self):
        time.sleep(self.sleep)
        try:
            print('Ready to send WhatsApp message')
            self.send_whatsapp_message()
        except Exception as e:
            print('Error occurred')
            print(e)


def get_dates_in_month(year, month):
    # Determine the first and last day of the month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    # Generate a list of dates for the month
    dates = []
    current_day = first_day

    while current_day <= last_day:
        dates.append(current_day.date())
        current_day += timedelta(days=1)

    return dates


def month_name_to_number(month_name):
    """ Convert month name to month number """
    try:
        return list(calendar.month_name).index(month_name)
    except ValueError:
        return None


def get_request():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            return request
    else:
        return None


def current_site(request=None):
    if not request:
        request = get_request()
    try:
        return get_current_site(request=request)
    except Exception as e:
        print(e)
        return None


def current_org(request=None):
    if not request:
        request = get_request()
    try:
        return current_site().organization
    except Exception as e:
        print(e)
        return None


def has_group(user, group_name):
    return user.groups.filter(name__iexact=group_name).exists()


entry_per_page = 500


def get_query_str(self):
    query = self.request.GET.get('query')
    if query is not None and query != "":
        query = query.strip()
        return query
    else:
        return False


def get_page_context(self, queryset=None):
    page_number = 1
    total_entry = 0
    context = {}
    page_count_start = 1
    if queryset:
        total_entry = queryset.count()
        page_number = get_request().GET.get('page')
    elif self:
        total_entry = self.object_list.count()
        page_number = self.request.GET.get('page')
    try:
        if page_number and not page_number == '1':
            current_page = int(page_number)
            i = 2
            while i <= current_page:
                page_count_start += entry_per_page
                i += 1
    except PageNotAnInteger:
        page_count_start = 1

    if total_entry == 0:
        page_count_start = 0
    page_count_end = page_count_start + entry_per_page - 1 if entry_per_page < total_entry else total_entry
    if page_count_end > total_entry:
        page_count_end -= abs(page_count_end - total_entry)
    context.update({'total_entry': total_entry})
    context.update({'page_count_start': page_count_start, 'page_count_end': page_count_end})
    return context


def nth_weekday_of_month(year, month, weekday, occurrence):
    first_day = datetime.date(year, month, 1)
    days_until_weekday = (weekday - first_day.weekday() + 7) % 7
    first_weekday = first_day + timedelta(days=days_until_weekday)
    nth_weekday = first_weekday + timedelta(weeks=occurrence - 1)
    if nth_weekday.month == month:
        return nth_weekday
    else:
        return None


def is_uuid(value):
    try:
        # Try to convert to UUID
        uuid.UUID(value)
        return True
    except ValueError:
        return False
