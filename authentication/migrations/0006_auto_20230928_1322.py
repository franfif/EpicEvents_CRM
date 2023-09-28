# Generated by Django 4.2.5 on 2023-09-28 13:22

from django.db import migrations


def create_user_roles_instances(apps, schema_editor):
    # Create an instance for each user role,
    # so that users can be created with a role
    UserRole = apps.get_model("authentication", "UserRole")

    ROLE_CHOICES = [
        ("SAL", "Sales Team"),
        ("SUP", "Support Team"),
        ("MAN", "Management"),
    ]

    for role_code, role_name in ROLE_CHOICES:
        UserRole.objects.create(role=role_code)


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0005_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(create_user_roles_instances),
    ]
