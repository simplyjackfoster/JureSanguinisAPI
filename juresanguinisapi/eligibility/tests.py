from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class EvaluateLineageAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_returns_evaluation_for_valid_payload(self):
        payload = {
            "applicant": {
                "id": "app",
                "name": "Applicant",
                "birth_date": "1990-07-01",
                "birth_country": "USA",
            },
            "ancestors": [
                {
                    "id": "a1",
                    "name": "Giorgio",
                    "birth_date": "1890-05-01",
                    "birth_country": "Italy",
                },
                {
                    "id": "a2",
                    "name": "Maria",
                    "birth_date": "1920-06-01",
                    "birth_country": "Argentina",
                },
            ],
            "lineage_links": [
                {"parent_id": "a1", "child_id": "a2", "relationship": "father"},
                {"parent_id": "a2", "child_id": "app", "relationship": "father"},
            ],
        }

        response = self.client.post(reverse("evaluate-lineage"), payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["overall_status"], "CLEAR_ADMIN_ELIGIBLE")
        self.assertEqual(response.data["acquisition_mode"], "AUTOMATIC_BY_BLOOD")
        self.assertFalse(response.data["needs_lawyer"])

    def test_returns_error_for_unknown_link_person(self):
        payload = {
            "applicant": {"id": "app", "name": "Applicant"},
            "ancestors": [],
            "lineage_links": [
                {"parent_id": "missing", "child_id": "app", "relationship": "father"}
            ],
        }

        response = self.client.post(reverse("evaluate-lineage"), payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown parent_id", str(response.data))
