from rest_framework.test import APITestCase

from authentication.models import UserRole, User


class UserTestApiCase(APITestCase):
    def test_manager_created_is_staff(self):
        test_user_created_is_staff_params = [
            (UserRole.MANAGEMENT, True),
            (UserRole.SALES_TEAM, False),
            (UserRole.SUPPORT_TEAM, False),
        ]
        for user_role, expected_is_staff in test_user_created_is_staff_params:
            with self.subTest(user_role=user_role, expected_is_staff=expected_is_staff):
                test_user = User.objects.create_user(
                    username=user_role,
                    email="test@epic.com",
                    role=UserRole.objects.get(role=user_role),
                    password="r0l3_73573r",
                )

                self.assertEqual(test_user.is_staff, expected_is_staff)
                self.assertEqual(test_user.is_superuser, expected_is_staff)
