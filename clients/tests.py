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

        cls.test_client_1 = Client.objects.create(
            company_name="Apple",
            sales_contact=cls.test_user,
            first_name="Tim",
            last_name="Cook",
            email="tim.cook@apple.com",
            phone_number="5552342123",
        )
        cls.test_client_2 = Client.objects.create(
            company_name="Microsoft",
            sales_contact=cls.test_user,
            first_name="Bill",
            last_name="Gates",
            email="bill.gates@microsoft.com",
            phone_number="5554567859",
        )

    def format_datetime(self, value):
        if value:
            return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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

    def get_client_detail_data(self, client):
        return {
            "id": client.pk,
            "company_name": client.company_name,
            "status": client.status.pk,
            "sales_contact": client.sales_contact.pk,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone_number": client.phone_number,
            "mobile_number": client.mobile_number,
            "date_created": self.format_datetime(client.date_created),
            "date_updated": self.format_datetime(client.date_updated),
            "contracts": [{"id": contract.id} for contract in client.contracts.all()],
            "events": [{"id": event.id} for event in client.events.all()],
        }


class TestClient(ClientAPITestCase):
    url_list = reverse_lazy("client-list")

    def test_list(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.get_client_list_data([self.test_client_1, self.test_client_2]),
            response.json(),
        )

    def test_detail(self):
        url_detail = reverse_lazy("client-detail", kwargs={"id": self.test_client_1.id})

        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.get_client_detail_data(self.test_client_1), response.json()
        )

    def test_create(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(
            self.url_list,
            data={
                "company_name": "Microsoft",
                "first_name": "Bill",
                "last_name": "Gates",
                "email": "bill.gates@microsoft.com",
                "phone_number": 5551234567,
            },
        )

        expected = {
            "id": response.json()["id"],
            "company_name": "Microsoft",
            "first_name": "Bill",
            "last_name": "Gates",
            "email": "bill.gates@microsoft.com",
            "phone_number": "5551234567",
            "mobile_number": None,
        }
        self.assertEqual(response.json(), expected)

    def test_create_read(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(
            self.url_list,
            data={
                "company_name": "Microsoft",
                "first_name": "Bill",
                "last_name": "Gates",
                "email": "bill.gates@microsoft.com",
                "phone_number": 5551234567,
            },
        )

        expected = {
            "id": response.json()["id"],
            "company_name": "Microsoft",
            "first_name": "Bill",
            "last_name": "Gates",
            "email": "bill.gates@microsoft.com",
            "phone_number": "5551234567",
            "mobile_number": None,
        }
        self.assertEqual(response.json(), expected)

        url_detail = reverse_lazy("client-detail", kwargs={"id": response.json()["id"]})

        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.get_client_detail_data(Client.objects.get(id=response.json()["id"])),
            response.json(),
        )
