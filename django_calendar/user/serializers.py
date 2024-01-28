from django.contrib.auth.hashers import make_password

from core.serializers import CalendarPublicSerializer
from .models import CustomUser
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    calendar_set = CalendarPublicSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'calendar_set']


class CustomUserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']
