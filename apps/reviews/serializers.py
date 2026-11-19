from rest_framework import serializers

from .models import WeeklyReview


class WeeklyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReview
        fields = [
            "id",
            "iso_year",
            "iso_week",
            "reflection_good",
            "reflection_improve",
            "weekly_goal_text",
            "weekly_goal_achieved",
            "weekly_goal_reflection",
            "numbers_reviewed",
            "most_important_confirmed",
            "status",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["id", "iso_year", "iso_week", "created_at"]
