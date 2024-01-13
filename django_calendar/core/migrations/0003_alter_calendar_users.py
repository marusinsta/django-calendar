# Generated by Django 4.2.9 on 2024-01-12 23:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_calendar_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='users',
            field=models.ManyToManyField(default=[], to=settings.AUTH_USER_MODEL),
        ),
    ]