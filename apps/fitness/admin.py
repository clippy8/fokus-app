from django.contrib import admin

from .models import Exercise, ExerciseCategory, FoodLogEntry, Recipe, WorkoutSet


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "equipment_number", "active")
    list_filter = ("user", "active", "categories")


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ("user", "exercise", "day", "set_number", "reps", "weight_kg")
    list_filter = ("user", "exercise")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "calories_kcal_per_100g", "protein_g_per_100g")
    list_filter = ("user",)


@admin.register(FoodLogEntry)
class FoodLogEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "day", "name", "recipe", "amount_g", "calories_kcal", "protein_g")
    list_filter = ("user", "day")
