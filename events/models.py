from django.db import models
from django.conf import settings

from clients.models import Client
from contracts.models import Contract


class EventStatus(models.Model):
    STATUS_CHOICES = [
        ("CRE", "Created"),
        ("PRO", "In Process"),
        ("END", "Ended"),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=3, unique=True)

    def __str__(self):
        return dict(self.STATUS_CHOICES)[str(self.status)]


class Event(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="events")
    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, related_name="event"
    )
    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="events"
    )
    status = models.ForeignKey(EventStatus, on_delete=models.PROTECT)
    attendees = models.IntegerField()
    event_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)
