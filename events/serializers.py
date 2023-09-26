from rest_framework import serializers
from events.models import Event


class EventListSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "contract", "client", "status", "support_contact"]

    def get_client(self, obj):
        return obj.contract.client.pk


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "support_contact",
            "status",
            "attendees",
            "event_date",
            "notes",
        ]
