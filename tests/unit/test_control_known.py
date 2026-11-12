"""Inbox owners must supply the admission stem rule at construction."""

import pytest

from chupa.control import ControlInbox
from chupa.daemon import PauseConsumer


def test_inbox_requires_known():
    with pytest.raises(TypeError, match="known"):
        ControlInbox(journal=None, lifecycle_id="life", holds=lambda: set(), apply=lambda _: None, files=lambda: (), read=lambda _: b"")


def test_pause_consumer_requires_and_forwards_known():
    args = dict(journal=None, lifecycle_id="life", state_dir=None, fs=None, sleep=None, files=lambda: (), read=lambda _: b"")
    with pytest.raises(TypeError, match="known"):
        PauseConsumer(**args)
    consumer = PauseConsumer(**args, known=lambda stem: stem == "x")
    assert consumer.inbox.known("x") is True
    assert consumer.inbox.known("y") is False
