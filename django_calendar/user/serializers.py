from django.contrib.auth.hashers import make_password

from core.models import Calendar
from .models import CustomUser
from rest_framework import serializers


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ['id', 'name']


class CustomUserSerializer(serializers.ModelSerializer):
    calendar_set = CalendarSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'calendar_set']
