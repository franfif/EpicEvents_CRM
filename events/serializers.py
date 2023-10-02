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
    status_name = serializers.StringRelatedField(source="status")

    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "contract_name",
            "status",
            "status_name",
            "attendees",
            "event_date",
            "notes",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    contract = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    support_contact = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "contract",
            "status",
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

    def get_contract(self, obj):
        return {
            "id": obj.contract.pk,
            "client": obj.contract.client.company_name,
            "amount": obj.contract.amount,
        }

    def get_status(self, obj):
        return {
            "id": obj.status.pk,
            "status_name": obj.status.get_status_display(),
        }

    def get_support_contact(self, obj):
        try:
            return {
                "id": obj.support_contact.pk,
                "full_name": obj.support_contact.get_full_name(),
                "role": obj.support_contact.role.get_role_display(),
            }
        except AttributeError:
            return None


class EventStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = EventStatus
        fields = ["id", "status"]
