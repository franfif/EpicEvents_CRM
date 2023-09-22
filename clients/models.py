from django.db import models
from django.conf import settings


class ClientStatus(models.Model):
    PROSPECT = "PRO"
    EXISTING = "EXI"

    STATUS_CHOICES = [
        (PROSPECT, "Prospective Client"),
        (EXISTING, "Existing Client"),
    ]
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=3, unique=True, default="PRO"
    )

    def __str__(self):
        return dict(self.STATUS_CHOICES)[str(self.status)]


class Client(models.Model):
    company_name = models.CharField(max_length=250)
    status = models.ForeignKey(ClientStatus, on_delete=models.PROTECT)
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="clients"
    )
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)
