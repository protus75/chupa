"""Present on the defective base, before any machine edit."""

from app import replay

result = replay({"initial_state": {"score": 0}, "actions": [{"op": "add", "amount": 3}]})
assert result["final_state"]["score"] == 3, "add must increase score by 3"
assert result["defect"] is False
print("add regression passed")
