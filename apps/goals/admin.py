from django.contrib import admin

from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt, Todo


class MeilensteinInline(admin.TabularInline):
    model = Meilenstein
    extra = 0


@admin.register(Jahresziel)
class JahreszielAdmin(admin.ModelAdmin):
    list_display = ("user", "year", "title", "status")
    list_filter = ("user", "year", "status")
    inlines = [MeilensteinInline]


class ProjektInline(admin.TabularInline):
    model = Projekt
    extra = 0


@admin.register(Meilenstein)
class MeilensteinAdmin(admin.ModelAdmin):
    list_display = ("jahresziel", "title", "status", "target_date")
    list_filter = ("jahresziel", "status")
    inlines = [ProjektInline]


@admin.register(Projekt)
class ProjektAdmin(admin.ModelAdmin):
    list_display = ("meilenstein", "title", "status", "end_date")
    list_filter = ("status",)


@admin.register(ProjectWeekFocus)
class ProjectWeekFocusAdmin(admin.ModelAdmin):
    list_display = ("projekt", "iso_year", "iso_week")
    list_filter = ("iso_year", "iso_week")


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "status", "due_date", "projekt")
    list_filter = ("user", "status")
