from django.contrib import admin

from .models import Dokument, Genre, Notizeintrag


@admin.register(Dokument)
class DokumentAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "title", "genre", "status", "favorite", "rating")
    list_filter = ("user", "type", "status", "favorite")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("user", "name")
    list_filter = ("user",)


@admin.register(Notizeintrag)
class NotizeintragAdmin(admin.ModelAdmin):
    list_display = ("dokument", "created_at")
    list_filter = ("dokument__user",)
