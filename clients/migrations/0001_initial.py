# Generated by Django 4.2.5 on 2023-09-14 18:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("PRO", "Prospective Client"),
                            ("EXI", "Existing Client"),
                        ],
                        max_length=3,
                        unique=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=25)),
                ("last_name", models.CharField(blank=True, max_length=25)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "mobile_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(null=True)),
                (
                    "sales_contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="clients.clientstatus",
                    ),
                ),
            ],
        ),
    ]
