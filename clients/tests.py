from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from unittest import mock

from clients.models import Client, ClientStatus
from clients.mocks import mock_perform_update, TEST_UPDATE_TIME
from authentication.models import UserRole, User


class ClientAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = ClientStatus.objects.create(status=ClientStatus.PROSPECT)
        # ClientStatus.objects.create(status=ClientStatus.EXISTING)

        test_sales_team_role = UserRole.objects.create(role=UserRole.SALES_TEAM)
        test_support_team_role = UserRole.objects.create(role=UserRole.SUPPORT_TEAM)
        cls.test_sales_team_member = User.objects.create(
            username="sales_tester",
            email="test_sales@epic.com",
            role=test_sales_team_role,
            password="s@l3s_73573r",
        )
        cls.test_sales_team_member_2 = User.objects.create(
            username="sales_tester_2",
            email="test2_sales@epic.com",
            role=test_sales_team_role,
            password="s@l3s_73573r",
        )
        cls.test_support_team_member = User.objects.create(
            username="support_tester",
            email="test_support@epic.com",
            role=test_support_team_role,
            password="su990r7_73573r",
        )

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
        test_list_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # User with no client assigned
            (self.test_support_team_member, 200, []),
            # Authorized user
            (
                self.test_sales_team_member,
                200,
                self.get_client_list_data([self.test_client_1, self.test_client_2]),
            ),
        ]

        for test_user, expected_status_code, expected_json in test_list_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                if test_user:
                    self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_list)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_create(self):
        self.client.force_authenticate(user=self.test_sales_team_member)
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
        self.client.force_authenticate(user=self.test_sales_team_member)
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

        self.client.force_authenticate(user=self.test_sales_team_member)
        response = self.client.get(url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            self.get_client_detail_data(Client.objects.get(id=response.json()["id"])),
        )

    def test_detail(self):
        url_detail = reverse_lazy("client-detail", kwargs={"id": self.test_client_1.id})

        self.client.force_authenticate(user=self.test_sales_team_member)
        response = self.client.get(url_detail)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), self.get_client_detail_data(self.test_client_1)
        )

    @mock.patch("clients.views.ClientDetailAPIView.perform_update", mock_perform_update)
    def test_update(self):
        test_update_params = [
            # Unauthenticated used
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_support_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Unauthorized user with right role
            (
                self.test_sales_team_member_2,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized user
            (
                self.test_sales_team_member,
                200,
                {
                    "id": self.test_client_1.id,
                    "company_name": "Apple Inc.",
                    "first_name": "Timothy Donald",
                    "last_name": "Cook",
                    "email": "tim.cook@apple.com",
                    "phone_number": "55523421298",
                    "mobile_number": None,
                    "sales_contact": self.test_client_1.sales_contact.pk,
                    "contracts": [
                        {"id": contract.id}
                        for contract in self.test_client_1.contracts.all()
                    ],
                    "events": [
                        {"id": event.id} for event in self.test_client_1.events.all()
                    ],
                    "date_created": self.format_datetime(
                        self.test_client_1.date_created
                    ),
                    "date_updated": self.format_datetime(TEST_UPDATE_TIME),
                    "status": self.test_client_1.status.pk,
                },
            ),
        ]

        for test_user, expected_status_code, expected_json in test_update_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                if test_user:
                    self.client.force_authenticate(user=test_user)
                url_detail = reverse_lazy(
                    "client-detail", kwargs={"id": self.test_client_1.id}
                )

                response = self.client.put(
                    url_detail,
                    data={
                        "company_name": "Apple Inc.",
                        "sales_contact": self.test_sales_team_member.pk,
                        "first_name": "Timothy Donald",
                        "email": "tim.cook@apple.com",
                        "phone_number": "55523421298",
                    },
                )

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
