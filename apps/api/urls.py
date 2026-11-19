from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api_views import ProfileDetailAPIView
from apps.dailydash.api_views import DayRoutineCheckViewSet, DayViewSet, RoutineItemViewSet
from apps.goals.api_views import (
    JahreszielViewSet,
    MeilensteinViewSet,
    ProjectWeekFocusViewSet,
    ProjektViewSet,
    TodoViewSet,
)
from apps.habits.api_views import DailyHabitCheckViewSet, HabitViewSet, WeeklyHabitCheckViewSet
from apps.reviews.api_views import WeeklyReviewViewSet

router = DefaultRouter()
router.register("days", DayViewSet, basename="day")
router.register("routine-items", RoutineItemViewSet, basename="routine-item")
router.register("routine-checks", DayRoutineCheckViewSet, basename="routine-check")
router.register("habits", HabitViewSet, basename="habit")
router.register("daily-habit-checks", DailyHabitCheckViewSet, basename="daily-habit-check")
router.register("weekly-habit-checks", WeeklyHabitCheckViewSet, basename="weekly-habit-check")
router.register("jahresziele", JahreszielViewSet, basename="jahresziel")
router.register("meilensteine", MeilensteinViewSet, basename="meilenstein")
router.register("projekte", ProjektViewSet, basename="projekt")
router.register("project-week-focus", ProjectWeekFocusViewSet, basename="project-week-focus")
router.register("todos", TodoViewSet, basename="todo")
router.register("weekly-reviews", WeeklyReviewViewSet, basename="weekly-review")

urlpatterns = [
    path("profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),
    path("", include(router.urls)),
]
