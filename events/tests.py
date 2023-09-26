import datetime
import pytz

from tests.test_setup import ProjectAPITestCase


class EventAPITestCase(ProjectAPITestCase):
    def get_event_list_data(self, events):
        return [
            {
                "id": event.pk,
                "contract": event.contract.pk,
                "client": event.contract.client.pk,
                "status": event.status.pk,
                "support_contact": event.support_contact.pk,
            }
            for event in events
        ]

    def get_event_detail_data(self, event):
        return {
            "id": event.pk,
            "client": event.contract.client.pk,
            "contract": event.contract.pk,
            "status": event.status.pk,
            "support_contact": event.support_contact.pk,
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
                    "status": self.test_status_created.pk,
                    "attendees": 1500,
                    "event_date": "2023-12-31T00:00:00Z",
                    "notes": "New Year's Eve",
                    "support_contact": None,
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
                        "event_date": datetime.datetime(2023, 12, 31, tzinfo=pytz.utc),
                        "notes": "New Year's Eve",
                    },
                )
                try:
                    expected_json["id"] = response.json()["id"]
                except KeyError:
                    pass

                self.assertEqual(response.status_code, expected_status_code)
                self.assertEqual(response.json(), expected_json)
