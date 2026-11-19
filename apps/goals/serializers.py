from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt, Todo


class JahreszielSerializer(serializers.ModelSerializer):
    progress_percent = serializers.IntegerField(read_only=True)
    time_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Jahresziel
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "archived",
            "start_value",
            "current_value",
            "target_value",
            "progress_percent",
            "time_percent",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "progress_percent", "time_percent", "created_at", "updated_at"]

    def validate(self, attrs):
        merged = {**(self.instance.__dict__ if self.instance else {}), **attrs}
        instance = Jahresziel(
            pk=self.instance.pk if self.instance else None,
            user=self.context["request"].user,
            start_date=merged.get("start_date"),
            end_date=merged.get("end_date"),
            archived=merged.get("archived", False),
        )
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages if hasattr(exc, "messages") else str(exc))
        return attrs


class MeilensteinSerializer(serializers.ModelSerializer):
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meilenstein
        fields = [
            "id",
            "jahresziel",
            "title",
            "description",
            "deadline",
            "status",
            "start_value",
            "current_value",
            "target_value",
            "progress_percent",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "progress_percent", "created_at"]

    def validate(self, attrs):
        jahresziel = attrs.get("jahresziel", self.instance.jahresziel if self.instance else None)
        instance = Meilenstein(pk=self.instance.pk if self.instance else None, jahresziel=jahresziel)
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages if hasattr(exc, "messages") else str(exc))
        return attrs


class ProjektSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projekt
        fields = [
            "id",
            "meilenstein",
            "title",
            "description",
            "next_step",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectWeekFocusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectWeekFocus
        fields = ["id", "projekt", "iso_year", "iso_week", "created_at"]
        read_only_fields = ["id", "created_at"]


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "title", "description", "due_date", "projekt", "status", "completed_at", "created_at"]
        read_only_fields = ["id", "completed_at", "created_at"]
