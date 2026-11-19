from django.urls import path

from . import views

app_name = "dokumente"

urlpatterns = [
    path("", views.dokument_list, name="list"),
    path("add/", views.dokument_add, name="add"),
    path("<int:pk>/edit/", views.dokument_edit, name="edit"),
    path("<int:pk>/delete/", views.dokument_delete, name="delete"),
    path("<int:pk>/convert/", views.notiz_convert, name="notiz-convert"),
    path("<int:pk>/notizen/add/", views.notizeintrag_add, name="notizeintrag-add"),
    path("<int:pk>/notizen/download/", views.notizeintrag_download, name="notizeintrag-download"),
    path("notizen/<int:pk>/delete/", views.notizeintrag_delete, name="notizeintrag-delete"),
]
