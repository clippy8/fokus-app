from rest_framework import serializers

from .models import Dokument, Genre, Notizeintrag


class GenreField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        if not data:
            return None
        return Genre.get_or_create_by_name(self.context["request"].user, data)


class DokumentSerializer(serializers.ModelSerializer):
    genre = GenreField(slug_field="name", queryset=Genre.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Dokument
        fields = [
            "id",
            "type",
            "title",
            "genre",
            "status",
            "favorite",
            "rating",
            "comment",
            "url",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotizeintragSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notizeintrag
        fields = ["id", "dokument", "text", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_dokument(self, value):
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError("Ungültiges Dokument.")
        return value
