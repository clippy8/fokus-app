from django.urls import path

from . import views

app_name = "fitness"

urlpatterns = [
    path("", views.fitness_index, name="index"),

    path("exercises/", views.exercise_list, name="exercise-list"),
    path("exercises/add/", views.exercise_add, name="exercise-add"),
    path("exercises/<int:pk>/edit/", views.exercise_edit, name="exercise-edit"),
    path("exercises/<int:pk>/deactivate/", views.exercise_deactivate, name="exercise-deactivate"),
    path("exercises/<int:pk>/history/", views.exercise_history, name="exercise-history"),

    path("training/<str:date>/", views.workout_day, name="workout-day"),

    path("rezepte/", views.recipe_list, name="recipe-list"),
    path("rezepte/add/", views.recipe_add, name="recipe-add"),
    path("rezepte/<int:pk>/edit/", views.recipe_edit, name="recipe-edit"),

    path("essen/<str:date>/", views.food_day, name="food-day"),
    path("essen/<str:date>/add/", views.food_entry_add, name="food-entry-add"),
    path("essen/eintrag/<int:pk>/edit/", views.food_entry_edit, name="food-entry-edit"),
    path("essen/eintrag/<int:pk>/delete/", views.food_entry_delete, name="food-entry-delete"),
]
