from django.core.exceptions import ObjectDoesNotExist

from tests.test_setup import ProjectAPITestCase
from contracts.models import Contract, ContractStatus
from authentication.models import User


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
            return contract.event
        except ObjectDoesNotExist:
            return None

    def get_contract_detail_data(self, contract):
        return {
            "id": contract.pk,
            "client": contract.client.pk,
            "status": contract.status.pk,
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
            # User with no contract assigned
            (self.test_support_team_member, 200, []),
            # Authorized user
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
