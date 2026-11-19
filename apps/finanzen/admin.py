from django.contrib import admin

from .models import FinanceEntry


@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "name", "tag", "category", "amount")
    list_filter = ("user", "category")
