from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Day, DayRoutineCheck, RoutineItem
from .serializers import DayRoutineCheckSerializer, DaySerializer, RoutineItemSerializer
from .services import get_or_create_day


class DayViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = DaySerializer
    lookup_field = "date"

    def get_queryset(self):
        return Day.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def today(self, request):
        day = get_or_create_day(request.user, timezone.localdate())
        return Response(self.get_serializer(day).data)


class RoutineItemViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineItemSerializer
    filterset_fields = ["timing", "active"]

    def get_queryset(self):
        return RoutineItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DayRoutineCheckViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = DayRoutineCheckSerializer
    filterset_fields = ["day", "checked"]

    def get_queryset(self):
        return DayRoutineCheck.objects.filter(day__user=self.request.user)

    def perform_update(self, serializer):
        checked = serializer.validated_data.get("checked")
        extra = {"checked_at": timezone.now() if checked else None} if checked is not None else {}
        serializer.save(**extra)
