from django.db import models

from user.models import CustomUser


class Calendar(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(CustomUser, default=[])


class Event(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField()
