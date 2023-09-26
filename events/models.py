from django.db import models
from django.conf import settings

from clients.models import Client
from contracts.models import Contract


class EventStatus(models.Model):
    CREATED = "CRE"
    IN_PROCESS = "PRO"
    ENDED = "END"

    STATUS_CHOICES = [
        (CREATED, "Created"),
        (IN_PROCESS, "In Process"),
        (ENDED, "Ended"),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=3, unique=True)

    def __str__(self):
        return dict(self.STATUS_CHOICES)[str(self.status)]


class Event(models.Model):
    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, related_name="event"
    )
    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="events"
    )
    status = models.ForeignKey(EventStatus, on_delete=models.PROTECT)
    attendees = models.IntegerField(null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)
