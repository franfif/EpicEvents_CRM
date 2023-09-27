from django.utils import timezone
from rest_framework import generics, permissions

from contracts import serializers, models
from contracts.permissions import IsContactOrReadOnly

from authentication.models import UserRole


class ContractQuerysetMixin:
    def get_queryset(self):
        # Sales Team may access all contracts
        if self.request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM):
            return models.Contract.objects.all()
        # Support Team may only access contracts related to their events
        if self.request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM):
            return models.Contract.objects.filter(
                event__support_contact=self.request.user
            )


class ContractListCreateAPIView(ContractQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ContractCreateSerializer
        return serializers.ContractListSerializer

    def perform_create(self, serializer):
        # Give a default status to contract upon creation
        try:
            if serializer.validated_data["status"] is None:
                raise KeyError
        except KeyError:
            serializer.validated_data["status"] = models.ContractStatus.objects.get(
                status=models.ContractStatus.UNSIGNED
            )
        serializer.save()


class ContractDetailAPIView(ContractQuerysetMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]
    serializer_class = serializers.ContractDetailSerializer
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(date_updated=timezone.now())
