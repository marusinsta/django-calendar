from rest_framework import serializers

from user.models import CustomUser
from user.serializers import CustomUserSerializer
from .models import Calendar


class CalendarSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Calendar
        fields = ['id', 'name', 'users']

class CalendarUpdateSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Calendar
        fields = ['id', 'name', 'users']
