# Generated by Django 4.2.5 on 2023-10-05 15:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0008_alter_client_first_name_alter_client_last_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="clientstatus",
            options={"verbose_name_plural": "statuses"},
        ),
    ]
