from chupa.observe import live_call


def test_provider_process_labels():
    root = (10, 1, "chupa drain")
    assert live_call([root, (11, 10, "node /p/@qwen-code/qwen-code/cli-entry.js --auth-type openai -m qwen3-coder:30b -o stream-json")], 10) == "qwen qwen3-coder:30b"
    assert live_call([root, (11, 10, "node /p/@qwen-code/qwen-code/cli-entry.js")], 10) == "qwen ?"
    assert live_call([root, (11, 10, "codex exec -m gpt -c model_reasoning_effort=high")], 10) == "codex gpt (reasoning effort high)"
    assert live_call([root, (11, 10, "claude -p --model opus")], 10) == "claude opus"
