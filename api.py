
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

app = FastAPI(
    title="AI Workflow Orchestrator",
    description="API for automated case validation and workflow routing",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def home():
    return {"message": "AI Workflow Orchestrator API is running"}


@app.get("/cases/{case_id}")
def process_case(case_id: str):
    case_data = get_customer(case_id)

    if case_data is None:
        raise HTTPException(status_code=404, detail="Case not found")

    issues = validate_case(case_data)
    result = route_workflow(case_data, issues)

    state = create_workflow_state(
        case_id,
        result["status"],
        result["next_action"],
    )

    # Save each workflow result to SQLite
    save_workflow_result(
        case_id,
        result["status"],
        issues,
        result["next_action"],
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
    case_data = get_customer(case_id)

    if case_data is None:
        raise HTTPException(status_code=404, detail="Case not found")

    history = get_workflow_history(case_id)

    return {
        "case_id": case_id,
        "total_runs": len(history),
        "history": history,
    }
