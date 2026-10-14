
import unittest

from main import (
    get_customer,
    validate_case,
    route_workflow,
    create_workflow_state,
)


class TestWorkflow(unittest.TestCase):

    def test_existing_case_is_retrieved(self):
        case_data = get_customer("12345")
        self.assertIsNotNone(case_data)

    def test_missing_case_returns_none(self):
        self.assertIsNone(get_customer("99999"))

    def test_complete_case_is_valid(self):
        case_data = get_customer("12345")
        issues = validate_case(case_data)
        self.assertEqual(issues, [])

    def test_missing_document_requires_review(self):
        case_data = get_customer("56789")
        issues = validate_case(case_data)
        result = route_workflow(case_data, issues)

        self.assertEqual(result["status"], "REVIEW_REQUIRED")

    def test_workflow_state_contains_history(self):
        state = create_workflow_state(
            "12345",
            "VALIDATED",
            "Proceed to the next workflow stage",
        )

        self.assertEqual(state["case_id"], "12345")
        self.assertEqual(len(state["history"]), 3)


if __name__ == "__main__":
    unittest.main()
