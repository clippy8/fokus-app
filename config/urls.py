from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.dailydash.urls")),
    path("habits/", include("apps.habits.urls")),
    path("goals/", include("apps.goals.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
]
