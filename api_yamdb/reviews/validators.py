from django.utils import timezone
from rest_framework import serializers


def validate_year(value):
    if value > timezone.now().year:
        raise serializers.ValidationError('Год больше текущего!')
    return value
