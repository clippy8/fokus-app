from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.dailydash.urls")),
    path("habits/", include("apps.habits.urls")),
    path("goals/", include("apps.goals.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("fitness/", include("apps.fitness.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
