from datetime import datetime, timedelta, timezone
import unittest
from urllib.parse import quote

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_trial_status_expired_has_lockout(self):
        first_login_at = (datetime.now(timezone.utc) - timedelta(hours=73)).isoformat()
        response = self.client.get(
            f"/api/gym-owner/owner-1/trial-status?first_login_at={quote(first_login_at)}"
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["owner_id"], "owner-1")
        self.assertTrue(data["is_expired"])
        self.assertEqual(data["lockout_countdown_minutes"], 20)

    def test_provision_gym_owner_starts_clean_dashboard(self):
        response = self.client.post(
            "/api/provision/gym-owner",
            json={
                "id": "owner-2",
                "gmail": "owner2@example.com",
                "gym_name": "Gym A",
                "plan_type": "trial",
                "branch_location": "Mumbai",
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["owner"]["id"], "owner-2")
        self.assertEqual(data["dashboard"]["hiring"], [])
        self.assertEqual(data["dashboard"]["whatsapp"], [])


if __name__ == "__main__":
    unittest.main()
