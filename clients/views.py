from rest_framework import generics, permissions

from clients import serializers, models
from clients.permissions import IsContactOrReadOnly

from authentication.models import UserRole


class ClientListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]

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


class ClientDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsContactOrReadOnly]
    serializer_class = serializers.ClientDetailSerializer
    queryset = models.Client.objects.all()

    def get_object(self):
        obj = generics.get_object_or_404(self.get_queryset(), id=self.kwargs.get("id"))
        return obj
