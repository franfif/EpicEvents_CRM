from django.db import models
from django.conf import settings


class ClientStatus(models.Model):
    STATUS_CHOICES = [
        ("PRO", "Prospective Client"),
        ("EXI", "Existing Client"),
    ]
    role = models.CharField(choices=STATUS_CHOICES, max_length=3, unique=True)


class Client(models.Model):
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    status = models.ForeignKey(ClientStatus, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)
