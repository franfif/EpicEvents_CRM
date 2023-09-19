from rest_framework import generics, permissions

from clients import serializers, models
from clients.permissions import IsSalesTeamMemberOrReadOnly

from authentication.models import UserRole


class ClientListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSalesTeamMemberOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ClientCreateSerializer
        return serializers.ClientListSerializer

    def get_queryset(self):
        if self.request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM):
            return models.Client.objects.all()
        if self.request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM):
            return models.Client.objects.filter(
                contracts__event__support_contact=self.request.user
            )

    def perform_create(self, serializer):
        status = models.ClientStatus.objects.get(status="PRO")
        client = serializer.save(sales_contact=self.request.user)
        client.status = status
        client.save()

    # "status",
    # "sales_contact",
