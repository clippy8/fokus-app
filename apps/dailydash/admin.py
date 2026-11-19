from django.contrib import admin

from .models import Day, DayRoutineCheck, RoutineItem


class DayRoutineCheckInline(admin.TabularInline):
    model = DayRoutineCheck
    extra = 0


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "updated_at")
    list_filter = ("user",)
    date_hierarchy = "date"
    inlines = [DayRoutineCheckInline]


@admin.register(RoutineItem)
class RoutineItemAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "timing", "order", "active")
    list_filter = ("user", "timing", "active")
