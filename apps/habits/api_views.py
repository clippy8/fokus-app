from rest_framework import viewsets

from .models import DailyHabitCheck, Habit, WeeklyHabitCheck
from .serializers import DailyHabitCheckSerializer, HabitSerializer, WeeklyHabitCheckSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    filterset_fields = ["frequency", "active"]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DailyHabitCheckViewSet(viewsets.ModelViewSet):
    serializer_class = DailyHabitCheckSerializer
    filterset_fields = ["habit", "day"]

    def get_queryset(self):
        return DailyHabitCheck.objects.filter(habit__user=self.request.user)


class WeeklyHabitCheckViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyHabitCheckSerializer
    filterset_fields = ["habit", "iso_year", "iso_week"]

    def get_queryset(self):
        return WeeklyHabitCheck.objects.filter(habit__user=self.request.user)
