from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.current, name="current"),
    path("history/", views.history, name="history"),
    path("<int:iso_year>/<int:iso_week>/", views.detail, name="detail"),
]
