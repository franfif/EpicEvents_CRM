from rest_framework import serializers
from events.models import Event, EventStatus


class EventListSerializer(serializers.ModelSerializer):
    contract = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    support_contact = serializers.StringRelatedField()

    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "status",
            "support_contact",
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    contract_name = serializers.StringRelatedField(source="contract")
    support_contact = serializers.StringRelatedField()
    status_name = serializers.StringRelatedField(source="status")

    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "contract_name",
            "status",
            "status_name",
            "support_contact",
            "attendees",
            "event_date",
            "notes",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    contract = serializers.StringRelatedField()
    status_name = serializers.StringRelatedField(source="status")
    support_contact = serializers.StringRelatedField()

    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "status",
            "status_name",
            "support_contact",
            "attendees",
            "event_date",
            "notes",
            "date_created",
            "date_updated",
        ]
        read_only_fields = [
            "contract",
            "client",
            "support_contact",
            "date_created",
            "date_updated",
        ]


class EventStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = EventStatus
        fields = ["id", "status"]
