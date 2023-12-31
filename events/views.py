from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "contract__client__company_name",
        "contract__client__first_name",
        "contract__client__last_name",
        "contract__client__email",
    ]
    search_fields = [
        "contract__client__company_name",
        "contract__client__first_name",
        "contract__client__last_name",
        "contract__client__email",
        "event_date",
    ]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.EventCreateSerializer
        return serializers.EventListSerializer

    def perform_create(self, serializer):
        # Check that the user trying to create the event is the client's sales contact
        sales_contact = serializer.validated_data["contract"].client.sales_contact
        if sales_contact == self.request.user:
            # Give a default status to event upon creation
            try:
                if serializer.validated_data["status"] is None:
                    raise KeyError
            except KeyError:
                serializer.validated_data["status"] = models.EventStatus.objects.get(
                    status=models.EventStatus.CREATED
                )
            serializer.save()
        else:
            # Deny permission to create event if user is not the client's sales_contact
            raise PermissionDenied


class EventDetailAPIView(EventQuerysetMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasEventPermissions]
    serializer_class = serializers.EventDetailSerializer
    lookup_field = "pk"

    def perform_update(self, serializer):
        serializer.save(date_updated=timezone.now())


class EventStatusListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasEventPermissions]
    serializer_class = serializers.EventStatusSerializer
    queryset = models.EventStatus.objects.all()
