from rest_framework import serializers

from .models import FinanceEntry


class FinanceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceEntry
        fields = ["id", "name", "tag", "amount", "timestamp", "category", "created_at"]
        read_only_fields = ["id", "created_at"]
