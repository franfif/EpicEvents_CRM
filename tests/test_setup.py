from django.urls import reverse_lazy
from rest_framework.test import APITestCase


from clients.models import Client, ClientStatus
from authentication.models import UserRole, User


class ProjectAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Defining User Roles
        test_sales_team_role = UserRole.objects.create(role=UserRole.SALES_TEAM)
        test_support_team_role = UserRole.objects.create(role=UserRole.SUPPORT_TEAM)

        # Defining Users
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
        cls.test_support_team_member = User.objects.create_user(
            username="support_tester",
            email="test_support@epic.com",
            role=test_support_team_role,
            password="su990r7_73573r",
        )

        # Defining Client Status
        ClientStatus.objects.create(status=ClientStatus.PROSPECT)
        cls.status_existing = ClientStatus.objects.create(status=ClientStatus.EXISTING)

        # Defining Clients
        cls.test_client_1 = Client.objects.create(
            company_name="Apple",
            sales_contact=cls.test_sales_team_member,
            first_name="Tim",
            last_name="Cook",
            email="tim.cook@apple.com",
            phone_number="5552342123",
        )
        cls.test_client_2 = Client.objects.create(
            company_name="Microsoft",
            sales_contact=cls.test_sales_team_member,
            first_name="Bill",
            last_name="Gates",
            email="bill.gates@microsoft.com",
            phone_number="5554567859",
        )

        # Defining Client Urls
        cls.url_client_list = reverse_lazy("client-list")
        cls.url_client_detail = reverse_lazy(
            "client-detail", kwargs={"id": cls.test_client_1.id}
        )

        cls.url_list = reverse_lazy("client-list")

    def format_datetime(self, value):
        if value:
            return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
