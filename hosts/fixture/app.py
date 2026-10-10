"""A tiny score game with intentionally planted host defects."""

import json
from pathlib import Path


def replay(record):
    settings = json.loads(Path(__file__).with_name("settings.json").read_text())
    score = expected = record["initial_state"]["score"]
    for action in record["actions"]:
        amount = action["amount"]
        match action["op"]:
            case "add":
                score += amount * settings["add_scale"]
                expected += amount
            case "bonus":
                score += amount * settings["bonus_scale"]
                expected += amount * 2
            case "spend":
                score += amount * settings["spend_sign"]
                expected -= amount
            case _:
                raise ValueError("unknown action; select add, bonus or spend")
        if settings["floor"]:
            score = max(0, score)
        expected = max(0, expected)
    return {"final_state": {"score": score}, "defect": score != expected}
