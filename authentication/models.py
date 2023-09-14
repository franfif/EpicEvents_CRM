from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.Model):
    ROLE_CHOICES = [
        ("SAL", "Sales Team"),
        ("SUP", "Support Team"),
        ("MAN", "Management"),
    ]
    role = models.CharField(choices=ROLE_CHOICES, max_length=3, unique=True)


class User(AbstractUser):
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)
