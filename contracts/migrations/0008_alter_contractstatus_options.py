# Generated by Django 4.2.5 on 2023-10-05 15:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0007_alter_contractstatus_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contractstatus",
            options={"verbose_name_plural": "contract statuses"},
        ),
    ]
