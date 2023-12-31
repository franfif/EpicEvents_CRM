# Generated by Django 4.2.5 on 2023-09-26 16:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("events", "0003_remove_event_client_alter_event_attendees_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="support_contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
