from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from contracts.models import Contract, ContractStatus


class ContractListSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    sales_contact = serializers.StringRelatedField(source="client.sales_contact")

    class Meta:
        model = Contract
        fields = ["id", "client", "status", "sales_contact"]


class ContractCreateSerializer(serializers.ModelSerializer):
    client_company_name = serializers.StringRelatedField(source="client")
    status_name = serializers.StringRelatedField(source="status")

    class Meta:
        model = Contract
        fields = [
            "id",
            "client",
            "client_company_name",
            "status",
            "status_name",
            "amount",
            "payment_due",
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    client_company_name = serializers.StringRelatedField(source="client")
    status_name = serializers.StringRelatedField(source="status")
    sales_contact = serializers.SerializerMethodField(read_only=True)
    event = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            "id",
            "client",
            "client_company_name",
            "status",
            "status_name",
            "amount",
            "sales_contact",
            "payment_due",
            "date_created",
            "date_updated",
            "event_description",
        ]

    def get_sales_contact(self, obj):
        try:
            return {
                "id": obj.client.sales_contact.pk,
                "full_name": obj.client.sales_contact.get_full_name(),
                "role": obj.client.sales_contact.role.get_role_display(),
            }
        except AttributeError:
            return None

    def get_event(self, obj):
        try:
            return {
                'id': obj.event.pk,
                'event_date': obj.event.event_date,
                'attendees': obj.event.attendees,
            }
        except ObjectDoesNotExist:
            return None


class ContractStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ContractStatus
        fields = ["id", "status"]
