import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
ACP_JSON_DIR = REPO_ROOT / "ACP" / "ACP-JSONS"
PRIMARY_TEMPLATES = sorted(
    path
    for path in ACP_JSON_DIR.glob("agent-*.json")
    if path.name not in {"agent.json"}
)
ALL_JSON_TEMPLATES = sorted(path for path in ACP_JSON_DIR.glob("*.json"))
PLACEHOLDER_PREFIXES = ("__",)
FORBIDDEN_SECRET_PREFIXES = ("sk-", "sk-or-", "hf_", "sess-")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_server(path: Path) -> tuple[str, dict]:
    payload = load_json(path)
    servers = payload.get("agent_servers") or {}
    assert len(servers) == 1, f"{path.name} should define exactly one agent server"
    return next(iter(servers.items()))


def test_primary_templates_cover_all_provider_profile_pairs():
    names = {path.name for path in PRIMARY_TEMPLATES}
    expected = {
        "agent-huggingface-high.json",
        "agent-huggingface-low.json",
        "agent-local-openai-high.json",
        "agent-local-openai-low.json",
        "agent-ollama-high.json",
        "agent-ollama-low.json",
        "agent-openai-high.json",
        "agent-openai-low.json",
        "agent-openrouter-high.json",
        "agent-openrouter-low.json",
    }
    assert names == expected


def test_primary_templates_use_dedicated_low_high_executables():
    for path in PRIMARY_TEMPLATES:
        _, server = extract_server(path)
        command = server["command"]
        if path.name.endswith("-low.json"):
            assert command.endswith("openclaude-acp-low.exe"), path.name
        elif path.name.endswith("-high.json"):
            assert command.endswith("openclaude-acp-high.exe"), path.name
        else:
            raise AssertionError(f"Unexpected template name: {path.name}")


def test_primary_templates_match_declared_context_profile_and_provider():
    for path in PRIMARY_TEMPLATES:
        _, server = extract_server(path)
        env = server["env"]
        expected_profile = "low" if path.name.endswith("-low.json") else "high"
        expected_provider = path.name.removeprefix("agent-").removesuffix(".json").rsplit("-", 1)[0]

        assert env["OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE"] == expected_profile
        assert env["OPENCLAUDE_ACP_DEFAULT_WORKFLOW_MODE"] == "code"
        assert env["OPENCLAUDE_MODEL_PROVIDER"] == expected_provider.replace("-", "_")


def test_huggingface_templates_use_requested_router_model_and_token_name():
    for template_name in ("agent-huggingface-low.json", "agent-huggingface-high.json"):
        _, server = extract_server(ACP_JSON_DIR / template_name)
        env = server["env"]

        assert env["OPENAI_BASE_URL"] == "https://router.huggingface.co/v1"
        assert env["OPENAI_MODEL"] == "Qwen/Qwen3-Coder-Next-FP8:together"
        assert env["HF_TOKEN"] == "__SET_HUGGINGFACE_API_KEY__"
        assert "OPENAI_API_KEY" not in env


def test_all_json_templates_are_sanitized():
    for path in ALL_JSON_TEMPLATES:
        payload_text = path.read_text(encoding="utf-8")
        for secret_prefix in FORBIDDEN_SECRET_PREFIXES:
            assert secret_prefix not in payload_text, f"{path.name} contains a live secret-like token"

        payload = load_json(path)
        for _, server in (payload.get("agent_servers") or {}).items():
            env = server.get("env") or {}
            for key, value in env.items():
                if not isinstance(value, str):
                    continue
                if "KEY" in key or key.endswith("_TOKEN"):
                    assert value.startswith(PLACEHOLDER_PREFIXES) or value == "", (
                        f"{path.name} has non-placeholder credential value for {key}"
                    )


def test_generic_agent_preset_uses_low_wrapper():
    _, server = extract_server(ACP_JSON_DIR / "agent.json")
    env = server["env"]

    assert server["command"].endswith("openclaude-acp-low.exe")
    assert env["OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE"] == "low"
    assert env["OPENCLAUDE_MODEL_PROVIDER"] == "openrouter"


def test_legacy_sample_is_sanitized_and_explicitly_marked_compatibility():
    server_name, server = extract_server(ACP_JSON_DIR / "old.json")
    env = server["env"]

    assert "legacy compatibility" in server_name.lower()
    assert server["command"].endswith("openclaude-acp-modes.exe")
    assert env["OPEN_ROUTER_KEY"] == "__SET_OPENROUTER_KEY__"
