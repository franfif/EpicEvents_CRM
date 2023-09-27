from rest_framework import serializers
from contracts.models import Contract


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
    sales_contact = serializers.StringRelatedField(source="client.sales_contact")
    event = serializers.StringRelatedField()

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
            "event",
        ]
