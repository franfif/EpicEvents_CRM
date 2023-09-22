from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from contracts.models import Contract


class ContractListSerializer(serializers.ModelSerializer):
    sales_contact = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = ["id", "client", "status", "sales_contact"]

    def get_sales_contact(self, obj):
        return obj.client.sales_contact.pk


class ContractCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ["id", "client", "status", "amount", "payment_due"]


class ContractDetailSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    sales_contact = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            "id",
            "client",
            "status",
            "amount",
            "sales_contact",
            "payment_due",
            "date_created",
            "date_updated",
            "event",
        ]

    def get_event(self, obj):
        try:
            return obj.event
        except ObjectDoesNotExist:
            return None

    def get_sales_contact(self, obj):
        return obj.client.sales_contact.pk
