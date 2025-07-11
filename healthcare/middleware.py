import logging
import math
import zoneinfo

import pytz
import sweetify
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponsePermanentRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

from user.models import Attendance, WhiteIP

logger = logging.getLogger(__name__)


class RedirectWWWToNonWWWMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        # Check if the host starts with "www."
        if host.startswith("www."):
            non_www_host = host[4:]  # Strip "www."
            protocol = "https" if request.is_secure() else "http"
            new_url = f"{protocol}://{non_www_host}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)

        # Process the request as usual
        return self.get_response(request)


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = 'Asia/Kolkata'
        try:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        except Exception as e:
            logger.exception(e)
        try:
            timezone.activate(pytz.timezone(tzname))
        except pytz.UnknownTimeZoneError as e:
            logger.exception(e)
            timezone.deactivate()
        return self.get_response(request)


class CurrentOrgMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            site = get_current_site(request=request)
            request.site = site
        except Site.DoesNotExist:
            raise Http404("Site not found for this domain.")
        try:
            current_org = site.organization
            request.org = current_org
            user = request.user
            if user.is_authenticated:
                if not user.is_superuser:
                    if site != user.site:
                        protocol = request.scheme
                        full_url = f"{protocol}://{user.site.domain}{request.path}"
                        return redirect(full_url)

        except Exception as e:
            logger.exception(e)


class UnauthorizedAccessException(PermissionDenied):
    """Custom exception when user tries to access from an unauthorized IP."""
    pass


class AutoAttendanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'ip/add/whitelist' in request.path:
            return
        if request.user.is_authenticated:
            user_ip = self.get_client_ip(request)  # ✅ Get user IP
            site = Site.objects.get_current()  # ✅ Get current site
            today = now().date()
            user = request.user

            # ✅ Superuser & Admins can mark attendance from anywhere
            if user.is_superuser or user.groups.filter(name="admin").exists():
                self.mark_attendance(user, site, today, request)
                return  # ✅ Exit after marking attendance

            # ✅ Other users must be inside office (IP Whitelist)
            restricted_groups = {"employee", "doctor"}
            if user.groups.filter(name__in=restricted_groups).exists():
                if WhiteIP.objects.filter(ip=user_ip, site=site).exists():
                    self.mark_attendance(user, site, today, request)
                    return  # ✅ Exit after marking attendance

                # ❌ Deny access for unauthorized IPs
                return render(request, 'user/ip_blocked.html', {'ip': user_ip})

    def mark_attendance(self, user, site, today, request):
        """Marks attendance for the user if not already marked."""
        # Check if attendance for today is already marked
        if not Attendance.objects.filter(user=user, site=site, in_time__date=today).exists():
            # Mark attendance only if not already marked
            Attendance.objects.create(user=user, site=site, status='P')  # ✅ Mark attendance
            sweetify.success(request, title='Success', text="Your Attendance Successfully Captured.")
        else:
            # If attendance is already marked, no action
            pass


    def get_client_ip(self, request):
        """Extracts the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # ✅ First IP in case of proxy
        else:
            ip = request.META.get('REMOTE_ADDR')  # ✅ Direct client IP
        return ip
