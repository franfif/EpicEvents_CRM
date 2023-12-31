# Generated by Django 4.2.5 on 2023-09-28 15:08

from django.db import migrations


def create_contract_status_instances(apps, schema_editor):
    # Create an instance for each contract status,
    # so that contracts can be created with a status
    ContractStatus = apps.get_model("contracts", "ContractStatus")

    STATUS_CHOICES = [
        ("UNS", "Not Signed"),
        ("SIG", "Signed"),
        ("PYD", "Payed"),
    ]

    for status_code, status_name in STATUS_CHOICES:
        ContractStatus.objects.create(status=status_code)


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0005_alter_contract_status"),
    ]

    operations = [
        migrations.RunPython(create_contract_status_instances),
    ]
