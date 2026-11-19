from rest_framework import viewsets

from .models import Jahresziel, Meilenstein, ProjectWeekFocus, Projekt, Todo
from .serializers import (
    JahreszielSerializer,
    MeilensteinSerializer,
    ProjectWeekFocusSerializer,
    ProjektSerializer,
    TodoSerializer,
)


class JahreszielViewSet(viewsets.ModelViewSet):
    serializer_class = JahreszielSerializer
    filterset_fields = ["status", "archived"]

    def get_queryset(self):
        return Jahresziel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MeilensteinViewSet(viewsets.ModelViewSet):
    serializer_class = MeilensteinSerializer
    filterset_fields = ["jahresziel", "status"]

    def get_queryset(self):
        return Meilenstein.objects.filter(jahresziel__user=self.request.user)


class ProjektViewSet(viewsets.ModelViewSet):
    serializer_class = ProjektSerializer
    filterset_fields = ["meilenstein", "status"]

    def get_queryset(self):
        return Projekt.objects.filter(meilenstein__jahresziel__user=self.request.user)


class ProjectWeekFocusViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectWeekFocusSerializer
    filterset_fields = ["projekt", "iso_year", "iso_week"]

    def get_queryset(self):
        return ProjectWeekFocus.objects.filter(projekt__meilenstein__jahresziel__user=self.request.user)


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    filterset_fields = ["status", "projekt"]

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
