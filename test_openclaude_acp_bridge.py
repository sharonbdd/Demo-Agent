import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.openclaude_acp_bridge as bridge
from scripts.openclaude_acp_bridge import (
    OpenClaudeAgent,
    SessionState,
    apply_session_command,
    change_preview,
    is_tool_allowed_for_workflow,
    normalize_provider_auth_env,
    permission_prompt_title,
    parse_mode_id,
    preferred_shell_tool,
    runtime_platform,
    tools_arg_for_workflow,
    workflow_instruction,
)


@pytest.fixture
def temp_state_path(tmp_path, monkeypatch):
    path = tmp_path / "acp-state.json"
    monkeypatch.setenv("OPENCLAUDE_ACP_STATE_PATH", str(path))
    return path


def test_parse_mode_id_accepts_workflow_only_and_legacy_combined_ids():
    assert parse_mode_id("plan", "high") == ("high", "plan")
    assert parse_mode_id("low_fix") == ("low", "fix")
    assert parse_mode_id("HIGH_CODE".lower()) == ("high", "code")
    assert parse_mode_id("invalid") is None


def test_apply_session_command_updates_state_and_returns_remaining_prompt():
    state = SessionState(session_id="s1", cwd="F:/repo", context_profile="low", workflow_mode="code")

    changed, remainder = apply_session_command(state, "/high continue with analysis")

    assert changed is True
    assert remainder == "continue with analysis"
    assert state.context_profile == "high"
    assert state.workflow_mode == "code"

    changed, remainder = apply_session_command(state, "/plan draft the next steps")

    assert changed is True
    assert remainder == "draft the next steps"
    assert state.context_profile == "high"
    assert state.workflow_mode == "plan"

    changed, remainder = apply_session_command(state, "/brave proceed")

    assert changed is True
    assert remainder == "proceed"
    assert state.brave is True

    changed, remainder = apply_session_command(state, "/careful verify")

    assert changed is True
    assert remainder == "verify"
    assert state.brave is False


def test_tools_arg_for_ask_includes_ask_user_question():
    ask_tools = set((tools_arg_for_workflow("ask") or "").split(","))

    assert "AskUserQuestion" in ask_tools
    assert "Read" in ask_tools
    assert "Write" not in ask_tools


def test_session_state_to_json_ignores_live_process_handles():
    state = SessionState(session_id="session-live", cwd="F:/repo")
    state.active_process = object()

    payload = state.to_json()

    assert "active_process" not in payload
    assert payload["session_id"] == "session-live"
    assert payload["cwd"] == "F:/repo"
    assert payload["brave"] is False


def test_permission_preview_for_edit_tools_is_human_readable():
    payload = {
        "file_path": "src/app.ts",
        "old_string": "const value = oldValue",
        "new_string": "const value = newValue",
    }

    preview = change_preview("Edit", payload)
    title = permission_prompt_title("Edit", payload, "code")

    assert preview is not None
    assert "path=src/app.ts" in preview
    assert "old_string=" in preview
    assert title.startswith("CODE: Edit -> ")


def test_provider_auth_env_normalizes_huggingface_and_openrouter_keys():
    env = {
        "OPENCLAUDE_MODEL_PROVIDER": "huggingface",
        "HF_TOKEN": "hf-placeholder",
    }

    normalize_provider_auth_env(env)
    assert env["OPENAI_API_KEY"] == "hf-placeholder"

    env = {
        "OPENCLAUDE_MODEL_PROVIDER": "openrouter",
        "OPEN_ROUTER_KEY": "or-placeholder",
    }

    normalize_provider_auth_env(env)
    assert env["OPENAI_API_KEY"] == "or-placeholder"


def test_platform_helpers_and_workflow_instruction_reflect_windows(monkeypatch):
    monkeypatch.setattr(bridge.sys, "platform", "win32")

    state = SessionState(session_id="s", cwd="F:/repo", workflow_mode="code")
    instruction = workflow_instruction(state)

    assert runtime_platform() == "windows"
    assert preferred_shell_tool() == "PowerShell"
    assert "Platform: Windows" in instruction
    assert "Prefer the PowerShell tool" in instruction


def test_platform_helpers_and_workflow_instruction_reflect_linux(monkeypatch):
    monkeypatch.setattr(bridge.sys, "platform", "linux")

    state = SessionState(session_id="s", cwd="/repo", workflow_mode="code")
    instruction = workflow_instruction(state)

    assert runtime_platform() == "linux"
    assert preferred_shell_tool() == "Bash"
    assert "Platform: Linux" in instruction
    assert "Prefer the Bash tool" in instruction


@pytest.mark.parametrize(
    ("workflow_mode", "tool_name", "payload", "allowed"),
    [
        ("ask", "Read", {"file_path": "README.md"}, True),
        ("ask", "AskUserQuestion", {}, True),
        ("ask", "Write", {"file_path": "notes.md"}, False),
        ("ask", "Bash", {"command": "git status"}, False),
        ("plan", "Write", {"file_path": "PLAN.md"}, True),
        ("plan", "Edit", {"path": "docs/spec.md"}, True),
        ("plan", "Write", {"file_path": "src/main.ts"}, False),
        ("plan", "Bash", {"command": "pytest"}, False),
        ("fix", "Bash", {"command": "pytest"}, True),
        ("code", "Write", {"file_path": "src/main.ts"}, True),
    ],
)
def test_is_tool_allowed_for_workflow_matrix(workflow_mode, tool_name, payload, allowed):
    assert is_tool_allowed_for_workflow(tool_name, payload, workflow_mode) is allowed


def test_agent_persists_and_reloads_session_state(temp_state_path):
    agent = OpenClaudeAgent()
    state = SessionState(
        session_id="session-1",
        cwd="F:/PyCharm/Demo-Agent",
        model="gpt-4o-mini",
        context_profile="high",
        workflow_mode="fix",
        title="Investigate ACP persistence",
        has_started=True,
    )

    agent._persist_state(state)

    reloaded_agent = OpenClaudeAgent()
    restored = reloaded_agent.sessions["session-1"]

    assert temp_state_path.exists()
    assert restored.cwd == state.cwd
    assert restored.model == "gpt-4o-mini"
    assert restored.context_profile == "high"
    assert restored.workflow_mode == "fix"
    assert restored.title == "Investigate ACP persistence"
    assert restored.has_started is True


def test_build_command_uses_platform_specific_launcher(monkeypatch, temp_state_path):
    agent = OpenClaudeAgent()
    state = SessionState(session_id="session-3", cwd=str(Path.cwd()))
    fake_launcher = Path(__file__).resolve()
    monkeypatch.setattr(bridge, "launcher_path", lambda: fake_launcher)

    monkeypatch.setattr(bridge.sys, "platform", "win32")
    windows_command = agent._build_command(state, new_session=True)
    assert windows_command[:3] == ["cmd.exe", "/d", "/c"]
    assert str(fake_launcher) in windows_command

    monkeypatch.setattr(bridge.sys, "platform", "linux")
    linux_command = agent._build_command(state, new_session=True)
    assert linux_command[0] == str(fake_launcher)
    assert linux_command[1:3] == ["-p", "--verbose"]


def test_prompt_returns_user_visible_error_for_unknown_session():
    async def run():
        agent = OpenClaudeAgent()
        updates = []

        async def session_update(session_id, update, **kwargs):
            updates.append((session_id, update))

        agent.client = SimpleNamespace(session_update=session_update)

        response = await agent.prompt([], "missing-session")

        assert response.stop_reason == "end_turn"
        assert response.usage.total_tokens == 0
        assert updates
        assert "not found" in updates[-1][1].content.text.lower()

    asyncio.run(run())


def test_prompt_returns_user_visible_error_for_launch_failure(monkeypatch):
    async def run():
        agent = OpenClaudeAgent()
        updates = []

        async def session_update(session_id, update, **kwargs):
            updates.append((session_id, update))

        agent.client = SimpleNamespace(session_update=session_update)
        session = SessionState(session_id="launch-fail", cwd=str(Path.cwd()))
        agent.sessions[session.session_id] = session

        async def fail_create_subprocess(*args, **kwargs):
            raise OSError("launcher failed")

        monkeypatch.setattr(bridge.asyncio, "create_subprocess_exec", fail_create_subprocess)
        monkeypatch.setattr(bridge, "launcher_path", lambda: Path(__file__).resolve())

        response = await agent.prompt([], session.session_id)

        assert response.stop_reason == "end_turn"
        assert response.usage.total_tokens == 0
        assert updates
        assert "launch failed" in updates[-1][1].content.text.lower()

    asyncio.run(run())


def test_setters_keep_modes_and_config_options_in_sync(temp_state_path):
    async def run():
        agent = OpenClaudeAgent()
        response = await agent.new_session("F:/PyCharm/Demo-Agent")
        session_id = response.session_id

        await agent.set_session_mode("ask", session_id)
        state = agent.sessions[session_id]
        assert state.workflow_mode == "ask"
        assert state.mode_id == "ask"

        config_response = await agent.set_config_option("context_profile", session_id, "high")
        state = agent.sessions[session_id]
        assert state.context_profile == "high"
        assert state.mode_id == "ask"
        assert config_response is not None
        assert any(
            option.id == "context_profile" and option.currentValue == "high"
            for option in config_response.config_options
        )

        config_response = await agent.set_config_option("brave_mode", session_id, "on")
        state = agent.sessions[session_id]
        assert state.brave is True
        assert config_response is not None
        assert any(
            option.id == "brave_mode" and option.currentValue == "on"
            for option in config_response.config_options
        )

    asyncio.run(run())


def test_mode_state_exposes_only_four_workflow_modes(temp_state_path):
    agent = OpenClaudeAgent()
    state = SessionState(session_id="session-2", cwd=str(Path.cwd()))

    mode_state = agent._mode_state(state)

    assert mode_state.current_mode_id == "code"
    assert [mode.id for mode in mode_state.available_modes] == ["ask", "plan", "fix", "code"]
