from unittest import mock

from tests.test_setup import ProjectAPITestCase
from tests.mocks import mock_perform_update, TEST_UPDATE_TIME


class ContractAPITestCase(ProjectAPITestCase):
    def get_contract_list_data(self, contracts):
        return [
            {
                "id": contract.pk,
                "client": str(contract.client),
                "status": str(contract.status),
                "sales_contact": str(contract.client.sales_contact),
            }
            for contract in contracts
        ]

    def get_contract_detail_data(self, contract):
        return {
            "id": contract.pk,
            "client": contract.client.pk,
            "client_company_name": str(contract.client),
            "status": contract.status.pk,
            "status_name": str(contract.status),
            # format amount to match model format
            "amount": f"{float(contract.amount):.2f}",
            "sales_contact": self.get_contact(contract.client.sales_contact),
            "payment_due": contract.payment_due,
            "date_created": self.format_datetime(contract.date_created),
            "date_updated": self.format_datetime(contract.date_updated),
            "event": contract.event.pk,
            "event_description": str(contract.event),
        }


class TestContract(ContractAPITestCase):
    def test_contract_list(self):
        test_contract_list_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Support User with no events assigned
            (self.test_support_team_member_3, 200, []),
            # Support User with events assigned
            (
                self.test_support_team_member,
                200,
                self.get_contract_list_data([self.test_contract_1]),
            ),
            # Sales user
            (
                self.test_sales_team_member,
                200,
                self.get_contract_list_data(
                    [self.test_contract_1, self.test_contract_2, self.test_contract_3]
                ),
            ),
        ]
        for test_user, expected_status_code, expected_json in test_contract_list_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_contract_list)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_contract_list_filter(self):
        test_contract_list_filter_params = [
            # Filtering with client's company name
            (
                "?client__company_name=Apple",
                self.get_contract_list_data([self.test_contract_1]),
            ),
            # Filtering with client's first name
            (
                "?client__first_name=Bill",
                self.get_contract_list_data(
                    [self.test_contract_2, self.test_contract_3]
                ),
            ),
            # Filtering with client's last name
            (
                "?client__last_name=Cook",
                self.get_contract_list_data([self.test_contract_1]),
            ),
            # Filtering with client's email
            (
                "?client__email=bill.gates@microsoft.com",
                self.get_contract_list_data(
                    [self.test_contract_2, self.test_contract_3]
                ),
            ),
            # Filtering with client's phone number
            # does not filter at all
            (
                "?client__phone_number=5554567859",
                self.get_contract_list_data(
                    [self.test_contract_1, self.test_contract_2, self.test_contract_3]
                ),
            ),
            # Filtering with payment due date
            (
                "?payment_due=2023-12-31",
                self.get_contract_list_data([self.test_contract_3]),
            ),
            # Filtering with amount
            (
                "?amount=30000",
                self.get_contract_list_data([self.test_contract_3]),
            ),
        ]
        for query_parameter_test, expected_json in test_contract_list_filter_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_sales_team_member)
                response = self.client.get(
                    self.url_contract_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_contract_list_search(self):
        test_contract_list_search_params = [
            # Searching for company name
            (
                "?search=Apple",
                self.get_contract_list_data([self.test_contract_1]),
            ),
            # Searching for first name
            (
                "?search=Bill",
                self.get_contract_list_data(
                    [self.test_contract_2, self.test_contract_3]
                ),
            ),
            # Searching for last name
            (
                "?search=Cook",
                self.get_contract_list_data([self.test_contract_1]),
            ),
            # Searching for email
            (
                "?search=@microsoft.com",
                self.get_contract_list_data(
                    [self.test_contract_2, self.test_contract_3]
                ),
            ),
            # Searching for phone number
            (
                "?search=5554567859",
                [],
            ),
            # Searching for payment due date
            (
                "?search=2023-12-31",
                self.get_contract_list_data([self.test_contract_3]),
            ),
            # Searching for amount
            (
                "?search=30000",
                self.get_contract_list_data([self.test_contract_3]),
            ),
        ]
        for query_parameter_test, expected_json in test_contract_list_search_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_sales_team_member)
                response = self.client.get(
                    self.url_contract_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_contract_create(self):
        test_contract_create_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_support_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized user (correct role) not assigned to client
            (
                self.test_sales_team_member_2,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized user (correct role)
            (
                self.test_sales_team_member,
                201,
                {
                    "client": self.test_client_1.pk,
                    "client_company_name": str(self.test_client_1),
                    "status": self.test_status_signed.pk,
                    "status_name": str(self.test_status_signed),
                    "amount": "25000.00",
                    "payment_due": "2023-09-07T00:00:00Z",
                },
            ),
        ]
        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_contract_create_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.post(
                    self.url_contract_list,
                    data={
                        "client": self.test_client_1.pk,
                        "status": self.test_status_signed.pk,
                        "amount": 25000.00,
                        "payment_due": "2023-09-07T00:00:00Z",
                    },
                )
                try:
                    expected_json["id"] = response.json()["id"]
                except KeyError:
                    pass

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_contract_detail(self):
        test_contract_detail_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Support user with wrong role, not assigned to event
            (
                self.test_support_team_member_2,
                404,
                {"detail": "Not found."},
            ),
            # Support user with wrong role, but assigned to event
            (
                self.test_support_team_member,
                200,
                self.get_contract_detail_data(self.test_contract_1),
            ),
            # Authorized Sales user not sales_contact
            (
                self.test_sales_team_member_2,
                200,
                self.get_contract_detail_data(self.test_contract_1),
            ),
            # Authorized user
            (
                self.test_sales_team_member,
                200,
                self.get_contract_detail_data(self.test_contract_1),
            ),
        ]

        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_contract_detail_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_contract_detail)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    @mock.patch(
        "contracts.views.ContractDetailAPIView.perform_update", mock_perform_update
    )
    def test_contract_update(self):
        test_contract_update_params = [
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
                    "id": self.test_contract_1.id,
                    "client": self.test_client_2.pk,
                    "client_company_name": str(self.test_client_2),
                    "status": self.test_status_signed.pk,
                    "status_name": str(self.test_status_signed),
                    "amount": "25000.00",
                    # Sales contact changes because client changes
                    "sales_contact": self.get_contact(self.test_sales_team_member_2),
                    "payment_due": "2023-09-08T00:00:00Z",
                    "date_created": self.format_datetime(
                        self.test_contract_1.date_created
                    ),
                    "date_updated": self.format_datetime(TEST_UPDATE_TIME),
                    "event": self.test_contract_1.event.pk,
                    "event_description": str(self.test_contract_1.event),
                },
            ),
        ]

        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_contract_update_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)

                response = self.client.put(
                    self.url_contract_detail,
                    data={
                        "client": self.test_client_2.pk,
                        "status": self.test_status_signed.pk,
                        "amount": "25000",
                        "payment_due": "2023-09-08T00:00:00Z",
                        "event": self.test_contract_1.event.pk,
                    },
                )
                # self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
