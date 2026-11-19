from rest_framework import serializers

from .models import Exercise, ExerciseCategory, FoodLogEntry, Recipe, WorkoutSet


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseCategory
        fields = ["id", "code", "name"]
        read_only_fields = ["id"]


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "equipment_number",
            "equipment_setting",
            "image",
            "categories",
            "active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = ["id", "exercise", "day", "set_number", "reps", "weight_kg", "created_at"]
        read_only_fields = ["id", "created_at"]


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "text", "image", "calories_kcal_per_100g", "protein_g_per_100g", "created_at"]
        read_only_fields = ["id", "created_at"]


class FoodLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodLogEntry
        fields = ["id", "day", "name", "recipe", "amount_g", "calories_kcal", "protein_g", "created_at"]
        read_only_fields = ["id", "created_at"]
