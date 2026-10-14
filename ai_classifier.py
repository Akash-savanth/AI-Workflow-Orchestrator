
import json
import ollama


MODEL_NAME = "llama3.2:1b"


def classify_issue(issue: str) -> dict:
    """
    Ask the local AI model to classify a workflow issue.
    The AI recommendation is advisory, not an approval decision.
    """

    prompt = f"""
You are an assistant for a case-management workflow.

Analyze this issue:
{issue}

Return only a JSON object with these fields:
{{
  "issue_category": "MISSING_DOCUMENT",
  "severity": "MEDIUM",
  "recommended_action": "REQUEST_DOCUMENT",
  "human_review_required": true
}}

Rules:
- Use the exact field names shown.
- Use JSON only.
- Missing required documents must always require human review.
- Never recommend automatic case approval.
"""

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
        format="json",
        stream=False,
        options={"temperature": 0},
    )

    result = json.loads(response["response"])

    required_fields = {
        "issue_category",
        "severity",
        "recommended_action",
        "human_review_required",
    }

    if not required_fields.issubset(result):
        raise ValueError("AI response is missing required fields")

    if not isinstance(result["human_review_required"], bool):
        raise ValueError("AI human_review_required must be a boolean")

    # Enforce this safeguard in Python, not just in the AI prompt.
    if "missing" in issue.lower() and "document" in issue.lower():
        result["human_review_required"] = True
        result["recommended_action"] = "REQUEST_DOCUMENT"

    return result
