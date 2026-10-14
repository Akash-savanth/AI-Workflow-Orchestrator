
import logging

from fastapi import FastAPI, HTTPException

from main import (
    get_customer,
    validate_case,
    route_workflow,
    create_workflow_state,
)
from database import (
    initialize_database,
    save_workflow_result,
    get_workflow_history,
)
from ai_classifier import classify_issue


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Workflow Orchestrator",
    description="Workflow automation with local AI decision support",
    version="1.2.0",
)


@app.on_event("startup")
def startup():
    initialize_database()
    logger.info("Workflow API started successfully")


@app.get("/")
def home():
    return {"message": "AI Workflow Orchestrator API is running"}


@app.get("/cases/{case_id}")
def process_case(case_id: str):
    case_data = get_customer(case_id)

    if case_data is None:
        logger.warning("Case not found: %s", case_id)
        raise HTTPException(status_code=404, detail="Case not found")

    issues = validate_case(case_data)
    result = route_workflow(case_data, issues)

    state = create_workflow_state(
        case_id,
        result["status"],
        result["next_action"],
    )

    save_workflow_result(
        case_id,
        result["status"],
        issues,
        result["next_action"],
    )

    logger.info(
        "Case %s processed with status %s",
        case_id,
        result["status"],
    )

    return {
        "case_id": case_data["case_id"],
        "customer_name": case_data["customer_name"],
        "status": result["status"],
        "issues": issues,
        "next_action": result["next_action"],
        "workflow_state": state,
    }


@app.get("/cases/{case_id}/history")
def case_history(case_id: str):
    if get_customer(case_id) is None:
        logger.warning("History requested for unknown case: %s", case_id)
        raise HTTPException(status_code=404, detail="Case not found")

    history = get_workflow_history(case_id)

    return {
        "case_id": case_id,
        "total_runs": len(history),
        "history": history,
    }


@app.get("/cases/{case_id}/ai-review")
def ai_review_case(case_id: str):
    case_data = get_customer(case_id)

    if case_data is None:
        logger.warning("AI review requested for unknown case: %s", case_id)
        raise HTTPException(status_code=404, detail="Case not found")

    issues = validate_case(case_data)
    workflow_result = route_workflow(case_data, issues)
    ai_result = None

    if issues:
        try:
            ai_result = classify_issue("; ".join(issues))
            logger.info("AI classification completed for case %s", case_id)

        except Exception:
            logger.exception(
                "AI classification failed for case %s; using workflow rules",
                case_id,
            )

            ai_result = {
                "available": False,
                "message": "AI classification unavailable; using workflow rules.",
            }

    # Enforce the safety rule independently of AI output.
    if issues:
        workflow_result["status"] = "REVIEW_REQUIRED"
        workflow_result["next_action"] = "Send case for human review"

        if ai_result is not None and "human_review_required" in ai_result:
            ai_result["human_review_required"] = True
            ai_result["recommended_action"] = "REQUEST_DOCUMENT"

    save_workflow_result(
        case_id,
        workflow_result["status"],
        issues,
        workflow_result["next_action"],
    )

    logger.info(
        "AI-review workflow completed for case %s with status %s",
        case_id,
        workflow_result["status"],
    )

    return {
        "case_id": case_id,
        "status": workflow_result["status"],
        "issues": issues,
        "next_action": workflow_result["next_action"],
        "ai_recommendation": ai_result,
        "human_approval_required": bool(issues),
    }
