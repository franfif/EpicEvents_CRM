from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from clients.models import Client, ClientStatus
from authentication.models import UserRole, User


class ClientAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = ClientStatus.objects.create(status=ClientStatus.PROSPECT)
        # ClientStatus.objects.create(status=ClientStatus.EXISTING)

        cls.test_role = UserRole.objects.create(role=UserRole.SALES_TEAM)
        cls.test_user = User.objects.create(
            username="sales_tester",
            email="test_sales@epic.com",
            role=cls.test_role,
            password="s@l3s_73573r",
        )

        cls.test_client = Client.objects.create(
            company_name="Apple",
            sales_contact=cls.test_user,
            first_name="Tim",
            last_name="Cook",
            email="tim.cook@apple.com",
            phone_number="5552342123",
        )

    def get_client_list_data(self, clients):
        return [
            {
                "id": client.pk,
                "company_name": client.company_name,
                "status": client.status.pk,
                "sales_contact": client.sales_contact.pk,
            }
            for client in clients
        ]


class TestClient(ClientAPITestCase):
    url = reverse_lazy("client-list")

    def test_list(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_client_list_data([self.test_client]), response.json())
