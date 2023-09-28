# Generated by Django 4.2.5 on 2023-09-28 14:51

from django.db import migrations


def create_original_manager_user(apps, schema_editor):
    # Create the original manager so that the user can use the project
    # and create other users
    User = apps.get_model("authentication", "User")
    UserRole = apps.get_model("authentication", "UserRole")

    User.objects.create_superuser(
        username="epic_manager",
        password="ZUbYvr2N+yRVLhk#",
        email="manager@epicevents.com",
        role=UserRole.objects.get(role="MAN"),
        first_name="Manager",
        last_name="EpicEvents",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0006_auto_20230928_1322"),
    ]

    operations = [
        migrations.RunPython(create_original_manager_user),
    ]
