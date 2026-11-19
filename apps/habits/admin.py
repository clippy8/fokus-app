from django.contrib import admin

from .models import DailyHabitCheck, Habit, WeeklyHabitCheck


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "frequency", "active")
    list_filter = ("user", "frequency", "active")


@admin.register(DailyHabitCheck)
class DailyHabitCheckAdmin(admin.ModelAdmin):
    list_display = ("habit", "day", "checked_at")
    list_filter = ("habit",)


@admin.register(WeeklyHabitCheck)
class WeeklyHabitCheckAdmin(admin.ModelAdmin):
    list_display = ("habit", "iso_year", "iso_week", "checked_at")
    list_filter = ("habit",)
