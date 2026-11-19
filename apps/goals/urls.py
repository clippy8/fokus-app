from django.urls import path

from . import views

app_name = "goals"

urlpatterns = [
    path("", views.jahresziel_list, name="list"),
    path("add/", views.jahresziel_add, name="jahresziel-add"),
    path("<int:pk>/edit/", views.jahresziel_edit, name="jahresziel-edit"),
    path("<int:pk>/archive/", views.jahresziel_archive, name="jahresziel-archive"),
    path("<int:jahresziel_pk>/meilensteine/add/", views.meilenstein_add, name="meilenstein-add"),
    path("meilensteine/<int:pk>/edit/", views.meilenstein_edit, name="meilenstein-edit"),
    path("meilensteine/<int:meilenstein_pk>/projekte/add/", views.projekt_add, name="projekt-add"),
    path("projekte/uebersicht/", views.projekt_timeline, name="projekt-timeline"),
    path("projekte/<int:pk>/edit/", views.projekt_edit, name="projekt-edit"),
    path("projekte/<int:pk>/toggle-focus/", views.projekt_toggle_focus, name="projekt-toggle-focus"),
    path("projekte/<int:pk>/update-dates/", views.projekt_update_dates, name="projekt-update-dates"),
    path("todos/", views.todo_list, name="todo-list"),
    path("todos/add/", views.todo_add, name="todo-add"),
    path("todos/<int:pk>/edit/", views.todo_edit, name="todo-edit"),
    path("todos/<int:pk>/toggle-done/", views.todo_toggle_done, name="todo-toggle-done"),
]
