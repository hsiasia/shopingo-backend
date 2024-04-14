# Generated by Django 4.2.11 on 2024-04-12 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator_id', models.CharField(max_length=8)),
                ('creator_name', models.CharField(max_length=16)),
                ('event_name', models.CharField(max_length=32)),
                ('company_name', models.CharField(max_length=32)),
                ('hashtag', models.JSONField()),
                ('location', models.CharField(max_length=32)),
                ('event_date', models.DateTimeField()),
                ('scale', models.CharField(max_length=32)),
                ('budget', models.IntegerField()),
                ('detail', models.TextField()),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(blank=True, null=True)),
                ('score', models.IntegerField()),
            ],
        ),
    ]
