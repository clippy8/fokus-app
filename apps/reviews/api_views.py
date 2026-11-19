from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WeeklyReview
from .serializers import WeeklyReviewSerializer
from .services import get_or_create_current_review


class WeeklyReviewViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyReviewSerializer
    filterset_fields = ["iso_year", "iso_week", "status"]

    def get_queryset(self):
        return WeeklyReview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        review, _, _ = get_or_create_current_review(request.user)
        return Response(self.get_serializer(review).data)
