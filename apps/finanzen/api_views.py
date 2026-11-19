from rest_framework import viewsets

from .models import FinanceEntry
from .serializers import FinanceEntrySerializer


class FinanceEntryViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceEntrySerializer
    filterset_fields = ["category"]

    def get_queryset(self):
        return FinanceEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
