
import json
import ollama


MODEL_NAME = "llama3.2:1b"

ALLOWED_CATEGORIES = {
    "MISSING_DOCUMENT",
    "OTHER",
}

ALLOWED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

ALLOWED_ACTIONS = {
    "REQUEST_DOCUMENT",
    "HUMAN_REVIEW",
}


def classify_issue(issue: str) -> dict:
    """
    Classify a workflow issue with local AI.
    The result is advisory; Python workflow rules remain authoritative.
    """

    if not isinstance(issue, str) or not issue.strip():
        raise ValueError("Issue must be a non-empty string")

    prompt = f"""
You are an assistant for a case-management workflow.

Classify this issue:
{issue}

Return a JSON object with exactly these fields:
{{
  "issue_category": "MISSING_DOCUMENT",
  "severity": "MEDIUM",
  "recommended_action": "REQUEST_DOCUMENT",
  "human_review_required": true
}}

Allowed issue_category values:
- MISSING_DOCUMENT
- OTHER

Allowed severity values:
- LOW
- MEDIUM
- HIGH

Allowed recommended_action values:
- REQUEST_DOCUMENT
- HUMAN_REVIEW

Rules:
- Return JSON only.
- Missing required documents always require human review.
- Never recommend automatic approval.
"""

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
        format="json",
        stream=False,
        options={"temperature": 0},
    )

    try:
        result = json.loads(response["response"])
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError("AI returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object")

    required_fields = {
        "issue_category",
        "severity",
        "recommended_action",
        "human_review_required",
    }

    if not required_fields.issubset(result):
        raise ValueError("AI response is missing required fields")

    if result["issue_category"] not in ALLOWED_CATEGORIES:
        raise ValueError("AI returned an unsupported issue category")

    if result["severity"] not in ALLOWED_SEVERITIES:
        raise ValueError("AI returned an unsupported severity")

    if result["recommended_action"] not in ALLOWED_ACTIONS:
        raise ValueError("AI returned an unsupported action")

    if not isinstance(result["human_review_required"], bool):
        raise ValueError("AI human_review_required must be a boolean")

    # Enforce missing-document safeguards in Python.
    normalized_issue = issue.lower()

    if "missing" in normalized_issue and "document" in normalized_issue:
        result["issue_category"] = "MISSING_DOCUMENT"
        result["recommended_action"] = "REQUEST_DOCUMENT"
        result["human_review_required"] = True

    return result
