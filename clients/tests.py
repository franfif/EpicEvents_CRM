from django.core.exceptions import ObjectDoesNotExist

from unittest import mock

from tests.test_setup import ProjectAPITestCase
from tests.mocks import mock_perform_update, TEST_UPDATE_TIME


class ClientAPITestCase(ProjectAPITestCase):
    def get_client_list_data(self, clients):
        return [
            {
                "id": client.pk,
                "company_name": client.company_name,
                "status": str(client.status),
                "sales_contact": str(client.sales_contact),
            }
            for client in clients
        ]

    def get_client_detail_data(self, client):
        return {
            "id": client.pk,
            "company_name": client.company_name,
            "status": client.status.pk,
            "status_name": str(client.status),
            "sales_contact": self.get_contact(client.sales_contact),
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone_number": client.phone_number,
            "mobile_number": client.mobile_number,
            "date_created": self.format_datetime(client.date_created),
            "date_updated": self.format_datetime(client.date_updated),
            "contracts_and_events": self.get_contracts_and_events_from_client(client),
        }

    def get_contracts_and_events_from_client(self, client):
        contracts_and_events = []
        for contract in client.contracts.all():
            contract_and_event = {
                "contract_id": contract.pk,
                "contract_status": str(contract.status),
                "contract_amount": f"{float(contract.amount):.2f}",
            }
            # Show event if it exists
            try:
                contract_and_event["event_id"] = contract.event.pk
                contract_and_event["event_status"] = str(contract.event.status)
                contract_and_event["event_date"] = self.format_datetime(
                    contract.event.event_date
                )
            except ObjectDoesNotExist:
                pass
            contracts_and_events.append(contract_and_event)
        return contracts_and_events


class TestClient(ClientAPITestCase):
    def test_client_list(self):
        test_client_list_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Support User with no event assigned
            (self.test_support_team_member_3, 200, []),
            # Support User with client's event assigned
            (
                self.test_support_team_member,
                200,
                self.get_client_list_data([self.test_client_1]),
            ),
            # Authorized user
            (
                self.test_sales_team_member,
                200,
                self.get_client_list_data([self.test_client_1, self.test_client_2]),
            ),
        ]

        for test_user, expected_status_code, expected_json in test_client_list_params:
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

    def test_client_list_filter(self):
        test_client_list_filter_params = [
            # Filtering with company name
            (
                "?company_name=Apple",
                self.get_client_list_data([self.test_client_1]),
            ),
            # Filtering with first name
            (
                "?first_name=Bill",
                self.get_client_list_data([self.test_client_2]),
            ),
            # Filtering with last name
            (
                "?last_name=Cook",
                self.get_client_list_data([self.test_client_1]),
            ),
            # Filtering with email
            (
                "?email=bill.gates@microsoft.com",
                self.get_client_list_data([self.test_client_2]),
            ),
            # Filtering with phone number
            # does not filter at all
            (
                "?phone_number=5554567859",
                self.get_client_list_data([self.test_client_1, self.test_client_2]),
            ),
        ]
        for query_parameter_test, expected_json in test_client_list_filter_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_sales_team_member)
                response = self.client.get(
                    self.url_client_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_client_list_search(self):
        test_client_list_search_params = [
            # Searching for company name
            (
                "?search=Apple",
                self.get_client_list_data([self.test_client_1]),
            ),
            # Searching for first name
            (
                "?search=Bill",
                self.get_client_list_data([self.test_client_2]),
            ),
            # Searching for last name
            (
                "?search=Cook",
                self.get_client_list_data([self.test_client_1]),
            ),
            # Searching for email
            (
                "?search=@microsoft.com",
                self.get_client_list_data([self.test_client_2]),
            ),
            # Searching for phone number
            (
                "?search=5554567859",
                [],
            ),
        ]
        for query_parameter_test, expected_json in test_client_list_search_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_sales_team_member)
                response = self.client.get(
                    self.url_client_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_client_create(self):
        test_client_create_params = [
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
                    "status": self.test_status_prospect.pk,
                    "status_name": str(self.test_status_prospect),
                    "first_name": "Bill",
                    "last_name": "Gates",
                    "email": "bill.gates@microsoft.com",
                    "phone_number": "5551234567",
                    "mobile_number": None,
                },
            ),
        ]
        for test_user, expected_status_code, expected_json in test_client_create_params:
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

    def test_client_detail(self):
        test_client_detail_params = [
            # Unauthenticated used
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Support user with no event assigned
            (
                self.test_support_team_member_3,
                404,
                {"detail": "Not found."},
            ),
            # Support user with events assigned
            (
                self.test_support_team_member,
                200,
                self.get_client_detail_data(self.test_client_1),
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

        for test_user, expected_status_code, expected_json in test_client_detail_params:
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
    def test_client_update(self):
        test_client_update_params = [
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
                    "status": self.test_status_existing.pk,
                    "status_name": str(self.test_status_existing),
                    "sales_contact": self.get_contact(self.test_client_1.sales_contact),
                    "first_name": "Timothy Donald",
                    "last_name": "Cook",
                    "email": "tim.cook@apple.com",
                    "phone_number": "55523421298",
                    "mobile_number": None,
                    "date_created": self.format_datetime(
                        self.test_client_1.date_created
                    ),
                    "date_updated": self.format_datetime(TEST_UPDATE_TIME),
                    "contracts_and_events": self.get_contracts_and_events_from_client(
                        self.test_client_1
                    ),
                },
            ),
        ]

        for test_user, expected_status_code, expected_json in test_client_update_params:
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
                        "last_name": "Cook",
                        "email": "tim.cook@apple.com",
                        "phone_number": "55523421298",
                        "status": self.test_status_existing.pk,
                    },
                )

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
