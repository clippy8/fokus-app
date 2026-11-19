from rest_framework import viewsets

from .models import Dokument, Notizeintrag
from .serializers import DokumentSerializer, NotizeintragSerializer


class DokumentViewSet(viewsets.ModelViewSet):
    serializer_class = DokumentSerializer
    filterset_fields = ["type", "status", "favorite"]

    def get_queryset(self):
        return Dokument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotizeintragViewSet(viewsets.ModelViewSet):
    serializer_class = NotizeintragSerializer
    filterset_fields = ["dokument"]

    def get_queryset(self):
        return Notizeintrag.objects.filter(dokument__user=self.request.user)
