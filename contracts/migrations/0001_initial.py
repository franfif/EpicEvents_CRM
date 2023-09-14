# Generated by Django 4.2.5 on 2023-09-14 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("clients", "0002_rename_role_clientstatus_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContractStatus",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("SIG", "Signed"),
                            ("UNS", "Not Signed"),
                            ("PYD", "Payed"),
                        ],
                        max_length=3,
                        unique=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contract",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=16)),
                ("Payment_due", models.DateTimeField(null=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(null=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="clients.client"
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contracts.contractstatus",
                    ),
                ),
            ],
        ),
    ]
