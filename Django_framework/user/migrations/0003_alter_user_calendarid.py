# Generated by Django 4.2.11 on 2024-05-08 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_user_calendarid_user_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="calendarId",
            field=models.CharField(max_length=100, null=True),
        ),
    ]