from rest_framework import serializers
from clients.models import Client, ClientStatus


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "company_name", "status", "sales_contact"]


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "mobile_number",
        ]


class ClientDetailSerializer(serializers.ModelSerializer):
    contracts = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "status",
            "sales_contact",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "mobile_number",
            "date_created",
            "date_updated",
            "contracts",
            "events",
        ]

    def get_contracts(self, obj):
        return [{"id": contract.id} for contract in obj.contracts.all()]

    def get_events(self, obj):
        return [{"id": event.id} for event in obj.events.all()]
