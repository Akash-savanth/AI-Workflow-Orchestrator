
from ai_classifier import classify_issue

result = classify_issue("Required document is missing.")

print("AI classification result:")
print(result)

assert result["issue_category"] == "MISSING_DOCUMENT"
assert result["human_review_required"] is True
assert result["recommended_action"] == "REQUEST_DOCUMENT"

print("AI classifier test passed!")
