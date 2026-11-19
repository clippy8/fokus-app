from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import DailyHabitCheck, Habit, WeeklyHabitCheck


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "frequency", "active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        instance = Habit(pk=self.instance.pk if self.instance else None, user=self.context["request"].user, **attrs)
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
        return attrs


class DailyHabitCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyHabitCheck
        fields = ["id", "habit", "day", "checked_at"]
        read_only_fields = ["id", "checked_at"]


class WeeklyHabitCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyHabitCheck
        fields = ["id", "habit", "iso_year", "iso_week", "checked_at"]
        read_only_fields = ["id", "checked_at"]
