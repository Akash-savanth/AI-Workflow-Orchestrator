
import unittest
import os
import tempfile

from fastapi.testclient import TestClient
import database
import api


class TestWorkflowAPI(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self.temp_db.close()

        self.original_db = database.DATABASE_NAME
        database.DATABASE_NAME = self.temp_db.name

        database.initialize_database()
        self.client = TestClient(api.app)

    
    def tearDown(self):
        self.client.close()

        # Close any SQLite connections before deleting the test database
        database.DATABASE_NAME = self.original_db

        import gc
        gc.collect()

        try:
            os.remove(self.temp_db.name)
        except PermissionError:
            pass

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_valid_case_is_processed_and_saved(self):
        response = self.client.get("/cases/12345")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "VALIDATED")

        history = self.client.get("/cases/12345/history").json()
        self.assertEqual(history["total_runs"], 1)

    def test_missing_document_requires_review(self):
        response = self.client.get("/cases/56789")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "REVIEW_REQUIRED")

    def test_unknown_case_returns_404(self):
        response = self.client.get("/cases/99999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
