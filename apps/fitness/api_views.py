from rest_framework import viewsets

from .models import Exercise, ExerciseCategory, FoodLogEntry, Recipe, WorkoutSet
from .serializers import (
    ExerciseCategorySerializer,
    ExerciseSerializer,
    FoodLogEntrySerializer,
    RecipeSerializer,
    WorkoutSetSerializer,
)


class ExerciseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    filterset_fields = ["active"]

    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkoutSetViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSetSerializer
    filterset_fields = ["exercise", "day"]

    def get_queryset(self):
        return WorkoutSet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FoodLogEntryViewSet(viewsets.ModelViewSet):
    serializer_class = FoodLogEntrySerializer
    filterset_fields = ["day", "recipe"]

    def get_queryset(self):
        return FoodLogEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
