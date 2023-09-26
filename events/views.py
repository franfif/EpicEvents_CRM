from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions

from events import serializers, models

from events.permissions import HasEventPermissions

from authentication.models import UserRole


class EventQuerysetMixin:
    def get_queryset(self):
        # Support Team may access all events
        if self.request.user.role == UserRole.objects.get(role=UserRole.SUPPORT_TEAM):
            return models.Event.objects.all()
        # Sales Team may only access events related to their clients
        if self.request.user.role == UserRole.objects.get(role=UserRole.SALES_TEAM):
            return models.Event.objects.filter(
                contract__client__sales_contact=self.request.user
            )


class EventListCreateAPIView(EventQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasEventPermissions]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.EventCreateSerializer
        return serializers.EventListSerializer

    def perform_create(self, serializer):
        # Check that the user trying to create the event is the client's sales contact
        sales_contact = serializer.validated_data["contract"].client.sales_contact
        if sales_contact == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied
