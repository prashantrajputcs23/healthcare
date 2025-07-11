from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.filter(Q(email=username) | Q(phone=username)).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None
