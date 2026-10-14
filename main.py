
import logging
from datetime import datetime, timezone


# Configure logging to the terminal and a log file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("workflow.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Synthetic sample cases for our project
CUSTOMER_CASES = {
    "12345": {
        "case_id": "12345",
        "customer_name": "Sample Customer A",
        "document_received": True
    },
    "56789": {
        "case_id": "56789",
        "customer_name": "Sample Customer B",
        "document_received": False
    }
}


# Tool 1: Retrieve a case
def get_customer(case_id):
    return CUSTOMER_CASES.get(case_id)


# Tool 2: Validate required documents
def validate_case(case_data):
    issues = []

    if not case_data.get("document_received"):
        issues.append("Required document is missing")

    return issues


# Workflow routing
def route_workflow(case_data, issues):
    if issues:
        return {
            "status": "REVIEW_REQUIRED",
            "next_action": "Send case for human review"
        }

    return {
        "status": "VALIDATED",
        "next_action": "Proceed to the next workflow stage"
    }


# Track workflow state and history
def create_workflow_state(case_id, status, next_action):
    return {
        "case_id": case_id,
        "status": status,
        "next_action": next_action,
        "history": [
            "Case received",
            "Validation completed",
            "Workflow route selected"
        ],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


# Main workflow
def main():
    case_id = input("Enter case ID (12345 or 56789): ").strip()

    logger.info("Received case ID: %s", case_id)

    # Retrieve the case
    case_data = get_customer(case_id)

    if case_data is None:
        logger.warning("Case not found: %s", case_id)
        print("Case not found.")
        return

    logger.info("Case retrieved successfully: %s", case_id)

    # Validate the case
    issues = validate_case(case_data)
    logger.info("Validation completed for case: %s", case_id)

    # Route the workflow
    workflow_result = route_workflow(case_data, issues)

    # Create workflow state
    workflow_state = create_workflow_state(
        case_id,
        workflow_result["status"],
        workflow_result["next_action"]
    )

    logger.info(
        "Workflow completed for case %s with status %s",
        case_id,
        workflow_result["status"]
    )

    # Display the results
    print("\n--- Workflow Result ---")
    print("Case ID:", case_data["case_id"])
    print("Customer:", case_data["customer_name"])
    print("Status:", workflow_result["status"])
    print("Issues:", issues)
    print("Next action:", workflow_result["next_action"])

    print("\n--- Workflow State ---")
    print(workflow_state)


if __name__ == "__main__":
    main()
