from unittest import mock

from tests.test_setup import ProjectAPITestCase
from tests.mocks import mock_perform_update, TEST_UPDATE_TIME


class ClientAPITestCase(ProjectAPITestCase):
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
                response = self.client.get(self.url_client_list)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_create(self):
        test_create_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_support_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized user (correct role)
            (
                self.test_sales_team_member,
                201,
                {
                    "company_name": "Microsoft",
                    "first_name": "Bill",
                    "last_name": "Gates",
                    "email": "bill.gates@microsoft.com",
                    "phone_number": "5551234567",
                    "mobile_number": None,
                },
            ),
        ]
        for test_user, expected_status_code, expected_json in test_create_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.post(
                    self.url_client_list,
                    data={
                        "company_name": "Microsoft",
                        "first_name": "Bill",
                        "last_name": "Gates",
                        "email": "bill.gates@microsoft.com",
                        "phone_number": 5551234567,
                    },
                )
                # The id will only be created if the instance is created (success)
                try:
                    expected_json["id"] = response.json()["id"]
                except KeyError:
                    pass

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_detail(self):
        test_detail_params = [
            # Unauthenticated used
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_support_team_member,
                404,
                {"detail": "Not found."},
            ),
            # Authorized Sales user not sales_contact
            (
                self.test_sales_team_member_2,
                200,
                self.get_client_detail_data(self.test_client_1),
            ),
            # Authorized user
            (
                self.test_sales_team_member,
                200,
                self.get_client_detail_data(self.test_client_1),
            ),
        ]

        for test_user, expected_status_code, expected_json in test_detail_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_client_detail)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

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
                    "status": self.status_existing.pk,
                },
            ),
        ]

        for test_user, expected_status_code, expected_json in test_update_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)

                response = self.client.put(
                    self.url_client_detail,
                    data={
                        "company_name": "Apple Inc.",
                        "sales_contact": self.test_sales_team_member.pk,
                        "first_name": "Timothy Donald",
                        "email": "tim.cook@apple.com",
                        "phone_number": "55523421298",
                        "status": self.status_existing.pk,
                    },
                )

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
