# Generated by Django 4.2.11 on 2024-04-14 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(max_length=32, primary_key=True, serialize=False),
        ),
    ]