from django.urls import path

from . import views

app_name = "habits"

urlpatterns = [
    path("", views.habit_list, name="list"),
    path("add/", views.habit_add, name="add"),
    path("<int:pk>/edit/", views.habit_edit, name="edit"),
    path("<int:pk>/deactivate/", views.habit_deactivate, name="deactivate"),
    path("<int:pk>/toggle-daily/<str:date>/", views.toggle_daily, name="toggle-daily"),
    path("<int:pk>/toggle-weekly/<int:iso_year>/<int:iso_week>/", views.toggle_weekly, name="toggle-weekly"),
]
