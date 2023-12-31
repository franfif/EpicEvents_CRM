from django.db import models
from clients.models import Client


class ContractStatus(models.Model):
    class Meta:
        verbose_name_plural = "contract statuses"

    UNSIGNED = "UNS"
    SIGNED = "SIG"
    PAYED = "PYD"

    STATUS_CHOICES = [
        (UNSIGNED, "Not Signed"),
        (SIGNED, "Signed"),
        (PAYED, "Payed"),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=3, unique=True)

    def __str__(self):
        return dict(self.STATUS_CHOICES)[str(self.status)]


class Contract(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contracts"
    )
    status = models.ForeignKey(ContractStatus, on_delete=models.PROTECT, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=16)
    payment_due = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.client}, {'{:.2f}'.format(self.amount)}"
