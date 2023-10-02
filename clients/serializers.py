from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from clients.models import Client, ClientStatus


class ClientListSerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField()
    sales_contact = serializers.StringRelatedField()

    class Meta:
        model = Client
        fields = ["id", "company_name", "status", "sales_contact"]


class ClientCreateSerializer(serializers.ModelSerializer):
    status_name = serializers.StringRelatedField(source="status")

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "status",
            "status_name",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "mobile_number",
        ]


class ClientDetailSerializer(serializers.ModelSerializer):
    status_name = serializers.StringRelatedField(source="status")
    sales_contact = serializers.StringRelatedField()
    contracts_and_events = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "status",
            "status_name",
            "sales_contact",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "mobile_number",
            "date_created",
            "date_updated",
            "contracts_and_events",
        ]

    def get_contracts_and_events(self, obj):
        contracts_and_events = []
        for contract in obj.contracts.all():
            contract_and_event = {
                "contract_id": contract.pk,
                "contract_status": str(contract.status),
                "contract_amount": f"{float(contract.amount):.2f}",
            }
            # Show event if it exists
            try:
                contract_and_event["event_id"] = contract.event.pk
                contract_and_event["event_status"] = str(contract.event.status)
                contract_and_event["event_date"] = contract.event.event_date
            except ObjectDoesNotExist:
                pass
            contracts_and_events.append(contract_and_event)
        return contracts_and_events


class ClientStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ClientStatus
        fields = ["id", "status"]
