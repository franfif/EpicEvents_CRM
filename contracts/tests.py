from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from unittest import mock

from contracts.models import Contract, ContractStatus
from authentication.models import User


class ContractAPISetup(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_sales_team_member = User.objects.create_user()


# class TestContract(ContractAPISetup):
#     def test_list(self):
#         self.client.force_authenticate(user=)
