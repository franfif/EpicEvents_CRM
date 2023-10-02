import datetime
import pytz
from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from authentication.models import UserRole, User
from clients.models import Client, ClientStatus
from contracts.models import Contract, ContractStatus
from events.models import Event, EventStatus


class ProjectAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Define User Roles
        test_sales_team_role = UserRole.objects.get(role=UserRole.SALES_TEAM)
        test_support_team_role = UserRole.objects.get(role=UserRole.SUPPORT_TEAM)

        # Define Users
        cls.test_sales_team_member = User.objects.create_user(
            username="sales_tester",
            email="test_sales@epic.com",
            role=test_sales_team_role,
            password="s@l3s_73573r",
        )
        cls.test_sales_team_member_2 = User.objects.create_user(
            username="sales_tester_2",
            email="test2_sales@epic.com",
            role=test_sales_team_role,
            password="s@l3s_73573r",
        )
        cls.test_sales_team_member_3 = User.objects.create_user(
            username="sales_tester_3",
            email="test3_sales@epic.com",
            role=test_sales_team_role,
            password="s@l3s_73573r",
        )
        cls.test_support_team_member = User.objects.create_user(
            username="support_tester",
            email="test_support@epic.com",
            role=test_support_team_role,
            password="su990r7_73573r",
        )
        cls.test_support_team_member_2 = User.objects.create_user(
            username="support_tester_2",
            email="test2_support@epic.com",
            role=test_support_team_role,
            password="su990r7_73573r",
        )
        cls.test_support_team_member_3 = User.objects.create_user(
            username="support_tester_3",
            email="test3_support@epic.com",
            role=test_support_team_role,
            password="su990r7_73573r",
        )

        # Define Client Status
        cls.test_status_prospect = ClientStatus.objects.get(
            status=ClientStatus.PROSPECT
        )
        cls.test_status_existing = ClientStatus.objects.get(
            status=ClientStatus.EXISTING
        )

        # Define Clients
        cls.test_client_1 = Client.objects.create(
            company_name="Apple",
            sales_contact=cls.test_sales_team_member,
            first_name="Tim",
            last_name="Cook",
            email="tim.cook@apple.com",
            phone_number="5552342123",
            status=cls.test_status_prospect,
        )
        cls.test_client_2 = Client.objects.create(
            company_name="Microsoft",
            sales_contact=cls.test_sales_team_member_2,
            first_name="Bill",
            last_name="Gates",
            email="bill.gates@microsoft.com",
            phone_number="5554567859",
            status=cls.test_status_prospect,
        )

        # Define Client Urls
        cls.url_client_list = reverse_lazy("client-list")
        cls.url_client_detail = reverse_lazy(
            "client-detail", kwargs={"pk": cls.test_client_1.id}
        )

        # Define Contract Status
        cls.test_status_unsigned = ContractStatus.objects.get(
            status=ContractStatus.UNSIGNED
        )
        cls.test_status_signed = ContractStatus.objects.get(
            status=ContractStatus.SIGNED
        )

        # Define Contracts
        cls.test_contract_1 = Contract.objects.create(
            client=cls.test_client_1,
            status=cls.test_status_unsigned,
            amount=10000,
        )
        cls.test_contract_2 = Contract.objects.create(
            client=cls.test_client_2,
            status=cls.test_status_unsigned,
            amount=20000,
        )
        cls.test_contract_3 = Contract.objects.create(
            client=cls.test_client_2,
            status=cls.test_status_unsigned,
            amount=30000,
            payment_due=datetime.datetime(2023, 12, 31, tzinfo=pytz.utc),
        )

        # Define Contract Urls
        cls.url_contract_list = reverse_lazy("contract-list")
        cls.url_contract_detail = reverse_lazy(
            "contract-detail", kwargs={"pk": cls.test_contract_1.id}
        )

        # Define Event Status
        cls.test_status_created = EventStatus.objects.get(status=EventStatus.CREATED)
        cls.test_status_in_process = EventStatus.objects.get(
            status=EventStatus.IN_PROCESS
        )
        cls.test_status_ended = EventStatus.objects.get(status=EventStatus.ENDED)

        # Define Events
        cls.test_event_1 = Event.objects.create(
            contract=cls.test_contract_1,
            support_contact=cls.test_support_team_member,
            status=cls.test_status_created,
            attendees=500,
            event_date=datetime.datetime(2024, 12, 25, microsecond=1, tzinfo=pytz.utc),
            notes="Christmas party!",
        )

        cls.test_event_2 = Event.objects.create(
            contract=cls.test_contract_2,
            support_contact=cls.test_support_team_member_2,
            status=cls.test_status_created,
        )

        # Define Event Urls
        cls.url_event_list = reverse_lazy("event-list")
        cls.url_event_detail = reverse_lazy(
            "event-detail", kwargs={"pk": cls.test_event_1.id}
        )

    def format_datetime(self, value):
        if value:
            return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def get_contact(self, contact):
        return {
            "id": contact.pk,
            "full_name": contact.get_full_name(),
            "role": contact.role.get_role_display(),
        }

    def get_contract(self, contract):
        return {
            "id": contract.pk,
            "client": contract.client.company_name,
            "amount": contract.amount,
        }
