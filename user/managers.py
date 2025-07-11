from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from healthcare.utils import current_site
from django.db.models import QuerySet


class UserManager(BaseUserManager):
    def site_user(self) -> QuerySet:
        """
        Returns a queryset of users filtered by the current site.
        """
        return self.get_queryset().filter(site=current_site())

    def create_user(self, email: str, password: str, **extra_fields) -> "User":
        """
        Creates and returns a new user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        current = current_site()  # Cache the current site value
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if current:
            user.site = current
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """
        Creates and returns a new superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
