import inspect

from chupa import tickets


def test_stems_is_a_required_keyword():
    parameter = inspect.signature(tickets.intake).parameters["stems"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
