from rest_framework import serializers

from user.models import CustomUser
from .models import Calendar, Event


class CalendarSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )

    owner = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Calendar
        fields = ['id', 'name', 'owner', 'users']


class CalendarPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ['id', 'name', 'owner']


class CalendarEmptySerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = []


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'calendar', 'name', 'description', 'timestamp']
