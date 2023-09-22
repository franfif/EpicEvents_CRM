from rest_framework import generics, permissions

from contracts import serializers, models
from authentication.models import UserRole

# from contract.permissions import

from datetime import datetime


class ContractQuerysetMixin:
    def get_queryset(self):
        if self.request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM):
            return models.Contract.objects.all()
        if self.request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM):
            return models.Contract.objects.filter(
                event__support_contact=self.request.user
            )


class ContractListCreateAPIView(ContractQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ContractCreateSerializer
        return serializers.ContractListSerializer


class ContractDetailAPIView(ContractQuerysetMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ContractDetailSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(date_updated=datetime.now())
