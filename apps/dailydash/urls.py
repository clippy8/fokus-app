from django.urls import path

from . import views

app_name = "dailydash"

urlpatterns = [
    path("", views.today, name="today"),
    path("day/<str:date>/", views.day_detail, name="day-detail"),
    path("day/<str:date>/routine/<int:check_id>/toggle/", views.toggle_routine_check, name="routine-check-toggle"),
    path("day/<str:date>/journal/", views.save_journal, name="journal-save"),
    path("history/", views.history_list, name="history"),
    path("routine-items/", views.routine_item_list, name="routine-item-list"),
    path("routine-items/add/", views.routine_item_add, name="routine-item-add"),
    path("routine-items/<int:pk>/edit/", views.routine_item_edit, name="routine-item-edit"),
    path("routine-items/<int:pk>/deactivate/", views.routine_item_deactivate, name="routine-item-deactivate"),
]
