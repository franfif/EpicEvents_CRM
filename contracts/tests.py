from django.core.exceptions import ObjectDoesNotExist
from unittest import mock

from tests.test_setup import ProjectAPITestCase
from tests.mocks import mock_perform_update, TEST_UPDATE_TIME


class ContractAPITestCase(ProjectAPITestCase):
    def get_contract_list_data(self, contracts):
        return [
            {
                "id": contract.pk,
                "client": contract.client.pk,
                "status": contract.status.pk,
                "sales_contact": contract.client.sales_contact.pk,
            }
            for contract in contracts
        ]

    def get_event(self, contract):
        try:
            return contract.event.pk
        except ObjectDoesNotExist:
            return None

    def get_contract_detail_data(self, contract):
        return {
            "id": contract.pk,
            "client": contract.client.pk,
            "status": contract.status.pk,
            # format amount to match model format
            "amount": f"{float(contract.amount):.2f}",
            "sales_contact": contract.client.sales_contact.pk,
            "payment_due": contract.payment_due,
            "date_created": self.format_datetime(contract.date_created),
            "date_updated": self.format_datetime(contract.date_updated),
            "event": self.get_event(contract),
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
                    [self.test_contract_1, self.test_contract_2]
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
            # Authorized user (correct role)
            (
                self.test_sales_team_member,
                201,
                {
                    "client": self.test_client_1.pk,
                    "status": self.test_status_signed.pk,
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
                    "status": self.test_status_signed.pk,
                    "amount": "25000.00",
                    # Sales contact changes because client changes
                    "sales_contact": self.test_sales_team_member_2.pk,
                    "payment_due": "2023-09-08T00:00:00Z",
                    "date_created": self.format_datetime(
                        self.test_contract_1.date_created
                    ),
                    "date_updated": self.format_datetime(TEST_UPDATE_TIME),
                    "event": self.get_event(self.test_contract_1),
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
                    },
                )
                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
