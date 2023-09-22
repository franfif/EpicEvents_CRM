from django.utils import timezone
from rest_framework import generics, permissions

from clients import serializers, models
from clients.permissions import IsContactOrReadOnly

from authentication.models import UserRole


class ClientQuerysetMixin:
    def get_queryset(self):
        if self.request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM):
            return models.Client.objects.all()
        if self.request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM):
            return models.Client.objects.filter(
                contracts__event__support_contact=self.request.user
            )


class ClientListCreateAPIView(ClientQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ClientCreateSerializer
        return serializers.ClientListSerializer

    def perform_create(self, serializer):
        status = models.ClientStatus.objects.get(status=models.ClientStatus.PROSPECT)
        serializer.save(sales_contact=self.request.user, status=status)


class ClientDetailAPIView(ClientQuerysetMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]
    serializer_class = serializers.ClientDetailSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(date_updated=timezone.now())
