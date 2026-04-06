import asyncio
import json
import os
from pathlib import Path

from acp import PROTOCOL_VERSION
from acp.client import ClientSideConnection
from acp.schema import AllowedOutcome, RequestPermissionResponse, TextContentBlock
from acp.stdio import spawn_agent_process


REPO_ROOT = Path(__file__).resolve().parent
ACP_JSON_DIR = REPO_ROOT / "ACP" / "ACP-JSONS"


def bridge_executable(name: str) -> Path:
    preferred = REPO_ROOT / "dist" / name
    updated = REPO_ROOT / "dist" / name.replace(".exe", "-updated.exe")
    if updated.exists():
        return updated
    return preferred


class RecordingClient:
    def __init__(self) -> None:
        self.updates: list[tuple[str, object]] = []

    def on_connect(self, conn: ClientSideConnection) -> None:
        self.conn = conn

    async def request_permission(self, options, session_id, tool_call, **kwargs):
        return RequestPermissionResponse(
            outcome=AllowedOutcome(
                outcome="selected",
                option_kind="allow_once",
                option_id="allow_once",
            )
        )

    async def session_update(self, session_id: str, update, **kwargs) -> None:
        self.updates.append((session_id, update))

    async def write_text_file(self, *args, **kwargs):
        return None

    async def read_text_file(self, *args, **kwargs):
        raise NotImplementedError

    async def create_terminal(self, *args, **kwargs):
        raise NotImplementedError

    async def terminal_output(self, *args, **kwargs):
        raise NotImplementedError

    async def release_terminal(self, *args, **kwargs):
        return None

    async def wait_for_terminal_exit(self, *args, **kwargs):
        raise NotImplementedError

    async def kill_terminal(self, *args, **kwargs):
        return None

    async def ext_method(self, method: str, params: dict):
        raise NotImplementedError

    async def ext_notification(self, method: str, params: dict) -> None:
        return None


def base_bridge_env(state_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["OPENCLAUDE_REPO_ROOT"] = str(REPO_ROOT)
    env["OPENCLAUDE_ACP_STATE_PATH"] = str(state_path)
    env["CLAUDE_CODE_USE_OPENAI"] = "1"
    env.setdefault("OPENAI_MODEL", "gpt-4o-mini")
    return env


async def connect_to_agent(command: str, env: dict[str, str]):
    client = RecordingClient()
    cm = spawn_agent_process(
        client,
        command,
        env=env,
        cwd=str(REPO_ROOT),
        use_unstable_protocol=True,
    )
    conn, process = await cm.__aenter__()
    try:
        init = await conn.initialize(PROTOCOL_VERSION)
        return cm, conn, process, client, init
    except Exception:
        await cm.__aexit__(None, None, None)
        raise


def assert_session_controls(response, expected_profile: str, expected_workflow: str):
    assert response.modes.current_mode_id == expected_workflow
    config_map = {option.id: option.currentValue for option in response.config_options}
    assert config_map["context_profile"] == expected_profile
    assert config_map["workflow_mode"] == expected_workflow


def test_low_high_executables_support_matrix_and_slash_commands(tmp_path):
    async def run():
        for executable_name, expected_profile in (
            ("openclaude-acp-low.exe", "low"),
            ("openclaude-acp-high.exe", "high"),
        ):
            state_path = tmp_path / f"{executable_name}.json"
            env = base_bridge_env(state_path)
            command = str(bridge_executable(executable_name))

            cm, conn, _process, client, init = await connect_to_agent(command, env)
            try:
                assert init.agent_info.name == "openclaude-acp"
                session = await conn.new_session(str(REPO_ROOT))
                session_id = session.session_id
                assert_session_controls(session, expected_profile, "code")

                for workflow in ("ask", "plan", "fix", "code"):
                    response = await conn.set_session_mode(workflow, session_id)
                    assert response is not None
                    loaded = await conn.load_session(str(REPO_ROOT), session_id)
                    assert_session_controls(loaded, expected_profile, workflow)

                for profile in ("low", "high"):
                    response = await conn.set_config_option(
                        "context_profile", session_id, profile
                    )
                    assert response is not None
                    loaded = await conn.load_session(str(REPO_ROOT), session_id)
                    assert_session_controls(loaded, profile, "code")

                prompt_response = await asyncio.wait_for(
                    conn.prompt(
                        [TextContentBlock(type="text", text="/plan")],
                        session_id,
                    ),
                    timeout=30,
                )
                assert prompt_response.stop_reason == "end_turn"
                reloaded = await conn.load_session(str(REPO_ROOT), session_id)
                assert_session_controls(reloaded, "high", "plan")
                assert any(
                    getattr(update, "sessionUpdate", None) == "current_mode_update"
                    for _, update in client.updates
                )
            finally:
                await cm.__aexit__(None, None, None)

    asyncio.run(run())


def test_session_list_and_load_survive_bridge_restart(tmp_path):
    async def run():
        state_path = tmp_path / "persistent-sessions.json"
        env = base_bridge_env(state_path)
        command = str(bridge_executable("openclaude-acp-low.exe"))

        cm1, conn1, _process1, _client1, _init1 = await connect_to_agent(command, env)
        try:
            session = await conn1.new_session(str(REPO_ROOT))
            session_id = session.session_id
            await conn1.set_config_option("workflow_mode", session_id, "fix")
            await conn1.set_config_option("context_profile", session_id, "high")
            await conn1.close_session(session_id)
        finally:
            await cm1.__aexit__(None, None, None)

        cm2, conn2, _process2, _client2, _init2 = await connect_to_agent(command, env)
        try:
            sessions = await conn2.list_sessions(cwd=str(REPO_ROOT))
            assert any(item.session_id == session_id for item in sessions.sessions)

            loaded = await conn2.load_session(str(REPO_ROOT), session_id)
            assert_session_controls(loaded, "high", "fix")

            resumed = await conn2.resume_session(str(REPO_ROOT), session_id)
            assert_session_controls(resumed, "high", "fix")
        finally:
            await cm2.__aexit__(None, None, None)

    asyncio.run(run())


def test_all_checked_in_acp_json_templates_launch(tmp_path):
    async def run():
        template_paths = sorted(ACP_JSON_DIR.glob("*.json"))
        for index, template_path in enumerate(template_paths):
            payload = json.loads(template_path.read_text(encoding="utf-8"))
            for _server_name, server in (payload.get("agent_servers") or {}).items():
                command = server["command"]
                env = os.environ.copy()
                env.update({k: str(v) for k, v in (server.get("env") or {}).items()})
                env["OPENCLAUDE_ACP_STATE_PATH"] = str(
                    tmp_path / f"{template_path.stem}-{index}.json"
                )

                cm, conn, _process, _client, init = await connect_to_agent(command, env)
                try:
                    assert init.agent_info.name == "openclaude-acp"
                    session = await conn.new_session(str(REPO_ROOT))
                    assert session.session_id
                finally:
                    await cm.__aexit__(None, None, None)

    asyncio.run(run())


def test_real_openrouter_prompt_if_key_is_available(tmp_path):
    if not (
        os.environ.get("OPEN_ROUTER_KEY")
        and os.environ.get("OPENCLAUDE_RUN_LIVE_PROVIDER_TESTS") == "1"
    ):
        return

    async def run():
        state_path = tmp_path / "openrouter-live.json"
        env = base_bridge_env(state_path)
        env["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
        env["OPENCLAUDE_MODEL_PROVIDER"] = "openrouter"
        env["OPENAI_MODEL"] = "qwen/qwen3.6-plus:free"
        command = str(bridge_executable("openclaude-acp-low.exe"))

        cm, conn, _process, _client, _init = await connect_to_agent(command, env)
        try:
            session = await conn.new_session(str(REPO_ROOT))
            response = await asyncio.wait_for(
                conn.prompt(
                    [TextContentBlock(type="text", text="Reply with the single word READY.")],
                    session.session_id,
                ),
                timeout=90,
            )
            assert response.stop_reason == "end_turn"
            assert response.usage is not None
        finally:
            await cm.__aexit__(None, None, None)

    asyncio.run(run())
