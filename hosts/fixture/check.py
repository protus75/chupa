"""Fast host smoke check; deliberately does not cover spending (the escape)."""

from app import replay

assert replay({"initial_state": {"score": 5}, "actions": []}) == {
    "final_state": {"score": 5}, "defect": False,
}
print("host smoke passed")
