import datetime
import pytz
from unittest import mock

from tests.test_setup import ProjectAPITestCase
from tests.mocks import mock_perform_update, TEST_UPDATE_TIME


class EventAPITestCase(ProjectAPITestCase):
    def get_event_list_data(self, events):
        return [
            {
                "id": event.pk,
                "contract": str(event.contract),
                "status": str(event.status),
                "support_contact": str(event.support_contact),
            }
            for event in events
        ]

    def get_event_detail_data(self, event):
        return {
            "id": event.pk,
            "contract": str(event.contract),
            "status": event.status.pk,
            "status_name": str(event.status),
            "support_contact": str(event.support_contact),
            "attendees": event.attendees,
            "event_date": self.format_datetime(event.event_date),
            "notes": event.notes,
            "date_created": self.format_datetime(event.date_created),
            "date_updated": self.format_datetime(event.date_updated),
        }


class TestEvent(EventAPITestCase):
    def test_event_list(self):
        test_event_list_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Authorized Sales user not assigned to clients with events
            (self.test_sales_team_member_3, 200, []),
            # Authorized Sales user assigned to clients with events
            # Sales users are able to see their clients' events
            (
                self.test_sales_team_member,
                200,
                self.get_event_list_data([self.test_event_1]),
            ),
            # Authorized Support user assigned to no event
            # Support users are able to see all the events
            (
                self.test_support_team_member_2,
                200,
                self.get_event_list_data([self.test_event_1, self.test_event_2]),
            ),
            # Authorized Support user assigned to events
            (
                self.test_support_team_member,
                200,
                self.get_event_list_data([self.test_event_1, self.test_event_2]),
            ),
        ]
        for test_user, expected_status_code, expected_json in test_event_list_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_event_list)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_event_list_filter(self):
        test_event_list_filter_params = [
            # Filtering with contract's client's company name
            (
                "?contract__client__company_name=Apple",
                self.get_event_list_data([self.test_event_1]),
            ),
            # Filtering with contract's client's first name
            (
                "?contract__client__first_name=Bill",
                self.get_event_list_data([self.test_event_2]),
            ),
            # Filtering with contract's client's last name
            (
                "?contract__client__last_name=Cook",
                self.get_event_list_data([self.test_event_1]),
            ),
            # Filtering with contract's client's email
            (
                "?contract__client__email=bill.gates@microsoft.com",
                self.get_event_list_data([self.test_event_2]),
            ),
            # Filtering with contract's client's phone number
            # does not filter at all
            (
                "?contract__client__phone_number=5554567859",
                self.get_event_list_data([self.test_event_1, self.test_event_2]),
            ),
            # Filtering with notes
            # does not filter at all
            (
                "?notes=Christmas party!",
                self.get_event_list_data([self.test_event_1, self.test_event_2]),
            ),
        ]
        for query_parameter_test, expected_json in test_event_list_filter_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_support_team_member)
                response = self.client.get(
                    self.url_event_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_event_list_search(self):
        test_event_list_search_params = [
            # Searching for company name
            (
                "?search=Apple",
                self.get_event_list_data([self.test_event_1]),
            ),
            # Searching for first name
            (
                "?search=Bill",
                self.get_event_list_data([self.test_event_2]),
            ),
            # Searching for last name
            (
                "?search=Cook",
                self.get_event_list_data([self.test_event_1]),
            ),
            # Searching for email
            (
                "?search=@microsoft.com",
                self.get_event_list_data([self.test_event_2]),
            ),
            # Searching for phone number
            (
                "?search=5554567859",
                [],
            ),
            # Searching for event date
            (
                "?search=2024-12-25",
                self.get_event_list_data([self.test_event_1]),
            ),
            # Searching for note
            # does not filter at all
            (
                "?search=Christmas party!",
                [],
            ),
        ]
        for query_parameter_test, expected_json in test_event_list_search_params:
            with self.subTest(
                query_parameter_test=query_parameter_test,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=self.test_support_team_member)
                response = self.client.get(
                    self.url_event_list + query_parameter_test,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected_json)

    def test_event_create(self):
        test_event_create_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_support_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Unauthorized Sales user (correct role but not assigned to the event's contract's client)
            (
                self.test_sales_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized Sales user (correct role to create event) assigned to event's contract
            (
                self.test_sales_team_member_2,
                201,
                {
                    "contract": self.test_contract_3.pk,
                    "contract_name": str(self.test_contract_3),
                    "status": self.test_status_created.pk,
                    "status_name": str(self.test_status_created),
                    "attendees": 1500,
                    "event_date": "2023-12-31T00:00:00.000001Z",
                    "notes": "New Year's Eve",
                },
            ),
            # Authorized Sales user assigned to event's contract to create another event for a contract
            (
                self.test_sales_team_member_2,
                400,
                {"contract": ["event with this contract already exists."]},
            ),
        ]
        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_event_create_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.post(
                    self.url_event_list,
                    data={
                        "contract": self.test_contract_3.pk,
                        "status": self.test_status_created.pk,
                        "attendees": 1500,
                        "event_date": datetime.datetime(
                            2023, 12, 31, microsecond=1, tzinfo=pytz.utc
                        ),
                        "notes": "New Year's Eve",
                    },
                )
                try:
                    expected_json["id"] = response.json()["id"]
                except KeyError:
                    pass

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    def test_event_detail(self):
        test_event_detail_params = [
            # Unauthenticated user
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Sales user with wrong role, not assigned to event's contract's client
            (
                self.test_sales_team_member_2,
                404,
                {"detail": "Not found."},
            ),
            # Sales user with wrong role, but assigned to event's contract's client
            (
                self.test_sales_team_member,
                200,
                self.get_event_detail_data(self.test_event_1),
            ),
            # Authorized Support user not support_contact
            (
                self.test_support_team_member_2,
                200,
                self.get_event_detail_data(self.test_event_1),
            ),
            # Authorized user
            (
                self.test_support_team_member,
                200,
                self.get_event_detail_data(self.test_event_1),
            ),
        ]

        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_event_detail_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)
                response = self.client.get(self.url_event_detail)

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)

    @mock.patch("events.views.EventDetailAPIView.perform_update", mock_perform_update)
    def test_event_update(self):
        test_event_update_params = [
            # Unauthenticated used
            (None, 401, {"detail": "Authentication credentials were not provided."}),
            # Unauthorized user with wrong role
            (
                self.test_sales_team_member,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Unauthorized user with right role
            (
                self.test_support_team_member_2,
                403,
                {"detail": "You do not have permission to perform this action."},
            ),
            # Authorized user
            (
                self.test_support_team_member,
                200,
                {
                    "id": self.test_event_1.pk,
                    "contract": str(self.test_event_1.contract),
                    "status": self.test_status_in_process.pk,
                    "status_name": str(self.test_status_in_process),
                    "support_contact": str(self.test_event_1.support_contact),
                    "attendees": 15000,
                    "event_date": self.format_datetime(
                        datetime.datetime(2024, 12, 31, microsecond=1, tzinfo=pytz.utc)
                    ),
                    "notes": "Christmas party 2024!",
                    "date_created": self.format_datetime(
                        self.test_event_1.date_created
                    ),
                    "date_updated": self.format_datetime(TEST_UPDATE_TIME),
                },
            ),
        ]

        for (
            test_user,
            expected_status_code,
            expected_json,
        ) in test_event_update_params:
            with self.subTest(
                test_user=test_user,
                expected_status_code=expected_status_code,
                expected_json=expected_json,
            ):
                self.client.force_authenticate(user=test_user)

                response = self.client.put(
                    self.url_event_detail,
                    data={
                        "status": self.test_status_in_process.pk,
                        "support_contact": self.test_event_1.support_contact.pk,
                        "attendees": 15000,
                        "event_date": datetime.datetime(
                            2024, 12, 31, microsecond=1, tzinfo=pytz.utc
                        ),
                        "notes": "Christmas party 2024!",
                    },
                )
                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
