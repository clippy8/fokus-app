from django.urls import path

from . import views

app_name = "finanzen"

urlpatterns = [
    path("", views.finance_list, name="list"),
    path("add/", views.finance_add, name="add"),
    path("<int:pk>/edit/", views.finance_edit, name="edit"),
    path("<int:pk>/delete/", views.finance_delete, name="delete"),
]
