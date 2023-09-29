from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.Model):
    SALES_TEAM = "SAL"
    SUPPORT_TEAM = "SUP"
    MANAGEMENT = "MAN"

    ROLE_CHOICES = [
        (SALES_TEAM, "Sales Team"),
        (SUPPORT_TEAM, "Support Team"),
        (MANAGEMENT, "Management"),
    ]
    role = models.CharField(choices=ROLE_CHOICES, max_length=3, unique=True)

    def __str__(self):
        return dict(self.ROLE_CHOICES)[str(self.role)]


class User(AbstractUser):
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.pk} - {self.first_name} {self.last_name}, {self.role}"

    def save(self, *args, **kwargs):
        # Ensure only a manager is staff even if role is changed in Admin
        is_manager = self.role == UserRole.objects.get(role=UserRole.MANAGEMENT)
        self.is_staff = is_manager
        self.is_superuser = is_manager
        super().save(*args, **kwargs)
