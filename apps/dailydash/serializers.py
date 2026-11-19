from rest_framework import serializers

from .models import Day, DayRoutineCheck, RoutineItem


class RoutineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineItem
        fields = ["id", "name", "timing", "order", "active", "created_at"]
        read_only_fields = ["id", "created_at"]


class DayRoutineCheckSerializer(serializers.ModelSerializer):
    routine_item_name = serializers.CharField(source="routine_item.name", read_only=True)

    class Meta:
        model = DayRoutineCheck
        fields = ["id", "day", "routine_item", "routine_item_name", "checked", "checked_at"]
        read_only_fields = ["id", "day", "routine_item", "routine_item_name", "checked_at"]


class DaySerializer(serializers.ModelSerializer):
    routine_checks = DayRoutineCheckSerializer(many=True, read_only=True)

    class Meta:
        model = Day
        fields = ["id", "date", "journal_text", "routine_checks", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
