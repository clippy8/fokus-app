from django.contrib import admin

from .models import WeeklyReview


@admin.register(WeeklyReview)
class WeeklyReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "iso_year", "iso_week", "status")
    list_filter = ("user", "status")
