
import unittest
import os
import tempfile
import gc

from unittest.mock import patch
from fastapi.testclient import TestClient

import database
import api


class TestWorkflowAPI(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary database for each test
        self.temp_db = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False,
        )
        self.temp_db.close()

        self.original_db = database.DATABASE_NAME
        database.DATABASE_NAME = self.temp_db.name

        database.initialize_database()
        self.client = TestClient(api.app)

    def tearDown(self):
        # Close the client and restore the original database path
        self.client.close()
        database.DATABASE_NAME = self.original_db

        # Collect unused objects before removing the temporary database
        gc.collect()

        try:
            os.remove(self.temp_db.name)
        except PermissionError:
            pass

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_valid_case_is_processed_and_saved(self):
        response = self.client.get("/cases/12345")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "VALIDATED")

        history_response = self.client.get("/cases/12345/history")

        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(history_response.json()["total_runs"], 1)

    def test_missing_document_requires_review(self):
        response = self.client.get("/cases/56789")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["status"],
            "REVIEW_REQUIRED",
        )

    def test_unknown_case_returns_404(self):
        response = self.client.get("/cases/99999")

        self.assertEqual(response.status_code, 404)

    @patch(
        "api.classify_issue",
        return_value={
            "issue_category": "MISSING_DOCUMENT",
            "severity": "MEDIUM",
            "recommended_action": "REQUEST_DOCUMENT",
            "human_review_required": True,
        },
    )
    def test_ai_review_requires_human_approval(self, mock_ai):
        response = self.client.get("/cases/56789/ai-review")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["status"], "REVIEW_REQUIRED")
        self.assertTrue(data["human_approval_required"])
        self.assertEqual(
            data["ai_recommendation"]["recommended_action"],
            "REQUEST_DOCUMENT",
        )
        mock_ai.assert_called_once()

    @patch(
        "api.classify_issue",
        side_effect=RuntimeError("Ollama unavailable"),
    )
    def test_ai_failure_keeps_case_in_review(self, mock_ai):
        response = self.client.get("/cases/56789/ai-review")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["status"], "REVIEW_REQUIRED")
        self.assertTrue(data["human_approval_required"])
        self.assertEqual(
            data["next_action"],
            "Send case for human review",
        )

    @patch("api.classify_issue")
    def test_valid_case_does_not_call_ai(self, mock_ai):
        response = self.client.get("/cases/12345/ai-review")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["status"], "VALIDATED")
        self.assertFalse(data["human_approval_required"])
        self.assertIsNone(data["ai_recommendation"])

        mock_ai.assert_not_called()


if __name__ == "__main__":
    unittest.main()
