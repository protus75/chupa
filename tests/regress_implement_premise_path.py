"""Reproduce acceptance of an Implement premise finding without a path."""

import json

from pydantic import ValidationError

from chupa.stages import ImplementReply

reply = {
    "outcome": "premise_failed",
    "summary": "unfinished",
    "surprises": "none",
    "dead_ends": "none",
    "predicted_vs_actual": "none",
    "findings": [{"code": "premise", "message": "unfinished", "paved_road": "finish"}],
}
try:
    ImplementReply.model_validate_json(json.dumps(reply))
except ValidationError:
    passed = True
else:
    passed = False
print(json.dumps({"regression_result": "pass" if passed else "defect"}))
raise SystemExit(0 if passed else 1)
