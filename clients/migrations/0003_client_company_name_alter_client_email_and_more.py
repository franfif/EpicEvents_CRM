# Generated by Django 4.2.5 on 2023-09-15 17:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("clients", "0002_rename_role_clientstatus_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="company_name",
            field=models.CharField(default="Company", max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="client",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="client",
            name="sales_contact",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="clients",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]