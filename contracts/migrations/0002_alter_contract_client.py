# Generated by Django 4.2.5 on 2023-09-15 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0003_client_company_name_alter_client_email_and_more"),
        ("contracts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contract",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contracts",
                to="clients.client",
            ),
        ),
    ]
