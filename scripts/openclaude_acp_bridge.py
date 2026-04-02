from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from acp import PROTOCOL_VERSION, run_agent
from acp.helpers import (
    start_tool_call,
    text_block,
    update_agent_message,
    update_agent_thought,
    update_tool_call,
)
from acp.schema import (
    AgentCapabilities,
    AuthenticateResponse,
    CloseSessionResponse,
    Implementation,
    InitializeResponse,
    ListSessionsResponse,
    LoadSessionResponse,
    ModelInfo,
    NewSessionResponse,
    PermissionOption,
    PromptCapabilities,
    PromptResponse,
    RequestPermissionResponse,
    SessionCapabilities,
    SessionCloseCapabilities,
    SessionInfo,
    SessionListCapabilities,
    SessionMode,
    SessionModeState,
    SessionModelState,
    SessionResumeCapabilities,
    ResumeSessionResponse,
    SetSessionConfigOptionResponse,
    SetSessionModeResponse,
    SetSessionModelResponse,
    Usage,
    AllowedOutcome,
    DeniedOutcome,
)


DEBUG = os.environ.get("OPENCLAUDE_ACP_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
}

DEFAULT_MODEL = "qwen/qwen3.6-plus:free"
READ_ONLY_TOOLS = [
    "Read",
    "Glob",
    "Grep",
    "WebFetch",
    "WebSearch",
    "ListMcpResources",
    "ReadMcpResource",
    "ToolSearch",
]


@dataclass(frozen=True)
class ModeConfig:
    mode_id: str
    name: str
    extra_args: tuple[str, ...] = ()


MODE_CONFIGS: dict[str, ModeConfig] = {
    "ask": ModeConfig(
        mode_id="ask",
        name="Ask",
        extra_args=(
            "--tools",
            "",
            "--disable-slash-commands",
        ),
    ),
    "plan": ModeConfig(
        mode_id="plan",
        name="Plan",
        extra_args=(
            "--tools",
            ",".join(READ_ONLY_TOOLS),
        ),
    ),
    "agent": ModeConfig(
        mode_id="agent",
        name="Agent",
        extra_args=(),
    ),
    "agent_full_access": ModeConfig(
        mode_id="agent_full_access",
        name="Agent (full access)",
        extra_args=(
            "--dangerously-skip-permissions",
        ),
    ),
}


def log(message: str) -> None:
    if DEBUG:
        print(f"[openclaude-acp] {message}", file=sys.stderr, flush=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_repo_root(start: Path) -> Path:
    override = os.environ.get("OPENCLAUDE_REPO_ROOT", "").strip()
    if override:
        candidate = Path(override).expanduser().resolve()
        if (candidate / "package.json").exists():
            return candidate
        raise FileNotFoundError(f"OPENCLAUDE_REPO_ROOT does not look like the repo root: {candidate}")

    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "package.json").exists() and (candidate / "bin" / "openclaude-openrouter.cmd").exists():
            return candidate
    raise FileNotFoundError(f"Could not locate repo root from {start}")


def repo_root() -> Path:
    if getattr(sys, "frozen", False):
        return _find_repo_root(Path(sys.executable).resolve().parent)
    return _find_repo_root(Path(__file__).resolve().parent)


def package_version() -> str:
    package_json = repo_root() / "package.json"
    try:
        return json.loads(package_json.read_text(encoding="utf-8"))["version"]
    except Exception:
        return "0.1.2"


def launcher_path() -> Path:
    override = os.environ.get("OPENCLAUDE_LAUNCHER", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / "bin" / "openclaude-openrouter.cmd"


def serialize_input(payload: dict[str, Any]) -> str:
    try:
        return json.dumps(payload, sort_keys=True, default=str)
    except TypeError:
        return repr(payload)


def tool_kind(tool_name: str) -> str:
    tool_map = {
        "Bash": "execute",
        "PowerShell": "execute",
        "Read": "read",
        "Write": "edit",
        "Edit": "edit",
        "NotebookEdit": "edit",
        "TodoWrite": "edit",
        "Glob": "search",
        "Grep": "search",
        "ToolSearch": "search",
        "WebFetch": "fetch",
        "Task": "other",
        "AskUserQuestion": "other",
    }
    return tool_map.get(tool_name, "other")


def extract_text_from_prompt(blocks: list[Any]) -> str:
    parts: list[str] = []
    for block in blocks:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            text = getattr(block, "text", "")
            if text:
                parts.append(text)
        elif block_type == "resource_link":
            uri = getattr(block, "uri", "")
            name = getattr(block, "name", "resource")
            parts.append(f"[resource:{name}] {uri}")
        elif block_type == "resource":
            resource = getattr(block, "resource", None)
            text = getattr(resource, "text", None)
            uri = getattr(resource, "uri", "embedded-resource")
            if text:
                parts.append(f"[resource:{uri}]\n{text}")
            else:
                parts.append(f"[resource:{uri}]")
        elif block_type == "image":
            parts.append("[image content omitted by OpenClaude ACP bridge]")
        elif block_type == "audio":
            parts.append("[audio content omitted by OpenClaude ACP bridge]")
    return "\n\n".join(part for part in parts if part).strip()


@dataclass
class SessionState:
    session_id: str
    cwd: str
    model: str = DEFAULT_MODEL
    mode_id: str = "agent"
    title: str | None = None
    updated_at: str = field(default_factory=now_iso)
    has_started: bool = False
    permission_cache: dict[str, str] = field(default_factory=dict)
    active_process: asyncio.subprocess.Process | None = None


class OpenClaudeAgent:
    def __init__(self) -> None:
        self.client = None
        self.sessions: dict[str, SessionState] = {}

    def on_connect(self, conn) -> None:
        self.client = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities=None,
        client_info=None,
        **kwargs: Any,
    ) -> InitializeResponse:
        log(f"initialize(protocol_version={protocol_version})")
        return InitializeResponse(
            protocol_version=PROTOCOL_VERSION,
            agent_info=Implementation(
                name="openclaude-openrouter-acp",
                title="OpenClaude via OpenRouter",
                version=package_version(),
            ),
            agent_capabilities=AgentCapabilities(
                load_session=True,
                prompt_capabilities=PromptCapabilities(
                    image=False,
                    audio=False,
                    embedded_context=False,
                ),
                session_capabilities=SessionCapabilities(
                    list=SessionListCapabilities(),
                    resume=SessionResumeCapabilities(),
                    close=SessionCloseCapabilities(),
                ),
            ),
            auth_methods=[],
        )

    async def new_session(self, cwd: str, mcp_servers=None, **kwargs: Any) -> NewSessionResponse:
        session_id = str(uuid4())
        state = SessionState(
            session_id=session_id,
            cwd=cwd,
            title=Path(cwd).name or cwd,
        )
        self.sessions[session_id] = state
        log(f"new_session({cwd}) -> {session_id}")
        return NewSessionResponse(
            session_id=session_id,
            modes=self._mode_state(state),
            models=self._model_state(state),
        )

    async def load_session(self, cwd: str, session_id: str, mcp_servers=None, **kwargs: Any) -> LoadSessionResponse:
        state = self.sessions.get(session_id)
        if state is None:
            state = SessionState(
                session_id=session_id,
                cwd=cwd,
                title=Path(cwd).name or cwd,
                has_started=True,
            )
            self.sessions[session_id] = state
        state.cwd = cwd
        state.updated_at = now_iso()
        return LoadSessionResponse(
            modes=self._mode_state(state),
            models=self._model_state(state),
        )

    async def resume_session(self, cwd: str, session_id: str, mcp_servers=None, **kwargs: Any) -> ResumeSessionResponse:
        state = self.sessions.get(session_id)
        if state is None:
            state = SessionState(
                session_id=session_id,
                cwd=cwd,
                title=Path(cwd).name or cwd,
                has_started=True,
            )
            self.sessions[session_id] = state
        state.cwd = cwd
        state.updated_at = now_iso()
        return ResumeSessionResponse(
            modes=self._mode_state(state),
            models=self._model_state(state),
        )

    async def list_sessions(self, cursor: str | None = None, cwd: str | None = None, **kwargs: Any) -> ListSessionsResponse:
        sessions = []
        for state in self.sessions.values():
            if cwd and state.cwd != cwd:
                continue
            sessions.append(
                SessionInfo(
                    session_id=state.session_id,
                    cwd=state.cwd,
                    title=state.title,
                    updated_at=state.updated_at,
                )
            )
        sessions.sort(key=lambda item: item.updated_at or "", reverse=True)
        return ListSessionsResponse(sessions=sessions, next_cursor=None)

    async def set_session_mode(self, mode_id: str, session_id: str, **kwargs: Any):
        state = self.sessions.get(session_id)
        if state is None:
            return None
        if mode_id not in MODE_CONFIGS:
            return None
        state.mode_id = mode_id
        return SetSessionModeResponse()

    async def set_session_model(self, model_id: str, session_id: str, **kwargs: Any):
        state = self.sessions.get(session_id)
        if state is None:
            return None
        state.model = model_id
        return SetSessionModelResponse()

    async def set_config_option(self, config_id: str, session_id: str, value: str | bool, **kwargs: Any):
        return SetSessionConfigOptionResponse()

    async def authenticate(self, method_id: str, **kwargs: Any):
        return AuthenticateResponse()

    async def close_session(self, session_id: str, **kwargs: Any):
        state = self.sessions.pop(session_id, None)
        if state and state.active_process and state.active_process.returncode is None:
            state.active_process.terminate()
            await state.active_process.wait()
        return CloseSessionResponse()

    async def cancel(self, session_id: str, **kwargs: Any) -> None:
        state = self.sessions.get(session_id)
        if state and state.active_process and state.active_process.returncode is None:
            log(f"cancel session {session_id}")
            state.active_process.terminate()

    async def prompt(
        self,
        prompt: list[Any],
        session_id: str,
        message_id: str | None = None,
        **kwargs: Any,
    ) -> PromptResponse:
        state = self.sessions.get(session_id)
        if state is None:
            raise RuntimeError(f"Unknown session: {session_id}")

        user_text = extract_text_from_prompt(prompt)
        if not user_text:
            user_text = "[empty prompt]"

        command = self._build_command(state, new_session=not state.has_started)

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=state.cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        state.active_process = process

        request_payload = {
            "type": "user",
            "session_id": state.session_id,
            "message": {"role": "user", "content": user_text},
            "parent_tool_use_id": None,
        }
        assert process.stdin is not None
        process.stdin.write((json.dumps(request_payload) + "\n").encode("utf-8"))
        await process.stdin.drain()
        process.stdin.close()

        stderr_task = asyncio.create_task(self._drain_stderr(process))
        stop_reason = "end_turn"
        usage = None
        try:
            assert process.stdout is not None
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                payload = self._parse_stdout_line(line)
                if payload is None:
                    continue
                payload_type = payload.get("type")
                if payload_type == "assistant":
                    await self._handle_assistant_message(session_id, payload)
                elif payload_type == "control_request":
                    await self._handle_control_request(state, process, payload)
                elif payload_type == "tool_progress":
                    await self._handle_tool_progress(session_id, payload)
                elif payload_type == "result":
                    stop_reason, usage = self._handle_result(payload)
                elif payload_type == "system":
                    await self._handle_system_message(state, payload)
            returncode = await process.wait()
            await stderr_task
            if returncode not in (0, 1):
                raise RuntimeError(f"OpenClaude exited with code {returncode}")
            state.has_started = True
        finally:
            state.active_process = None
            state.updated_at = now_iso()

        return PromptResponse(
            stop_reason=stop_reason,
            usage=usage,
            user_message_id=message_id,
        )

    def _build_command(self, state: SessionState, *, new_session: bool) -> list[str]:
        launcher = launcher_path()
        if not launcher.exists():
            raise FileNotFoundError(f"Launcher not found: {launcher}")

        args = [
            "cmd.exe",
            "/d",
            "/c",
            str(launcher),
            "-p",
            "--verbose",
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
        ]
        args.extend(MODE_CONFIGS.get(state.mode_id, MODE_CONFIGS["agent"]).extra_args)
        if new_session:
            args.extend(["--session-id", state.session_id])
        else:
            args.extend(["--resume", state.session_id])
        return args

    async def _drain_stderr(self, process: asyncio.subprocess.Process) -> None:
        if process.stderr is None:
            return
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if text:
                log(f"stderr: {text}")

    def _parse_stdout_line(self, line: bytes) -> dict[str, Any] | None:
        text = line.decode("utf-8", errors="replace").strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            log(f"non-json stdout: {text}")
            return None

    async def _handle_assistant_message(self, session_id: str, payload: dict[str, Any]) -> None:
        message = payload.get("message") or {}
        content = message.get("content") or []
        for block in content:
            block_type = block.get("type")
            if block_type == "text":
                await self.client.session_update(
                    session_id=session_id,
                    update=update_agent_message(text_block(block.get("text", ""))),
                )
            elif block_type in {"thinking", "redacted_thinking"}:
                thinking_text = block.get("thinking") or block.get("text") or ""
                if thinking_text:
                    await self.client.session_update(
                        session_id=session_id,
                        update=update_agent_thought(text_block(thinking_text)),
                    )
            elif block_type == "tool_use":
                await self.client.session_update(
                    session_id=session_id,
                    update=start_tool_call(
                        block.get("id", str(uuid4())),
                        title=block.get("name", "Tool"),
                        kind=tool_kind(block.get("name", "")),
                        status="pending",
                        raw_input=block.get("input"),
                    ),
                )

    async def _handle_control_request(
        self,
        state: SessionState,
        process: asyncio.subprocess.Process,
        payload: dict[str, Any],
    ) -> None:
        request = payload.get("request") or {}
        if request.get("subtype") != "can_use_tool":
            await self._write_control_response(
                process,
                {
                    "type": "control_response",
                    "response": {
                        "subtype": "error",
                        "request_id": payload["request_id"],
                        "error": f"Unsupported control request: {request.get('subtype')}",
                    },
                },
            )
            return

        cache_key = f"{request.get('tool_name')}::{serialize_input(request.get('input') or {})}"
        cached = state.permission_cache.get(cache_key)
        if cached is not None:
            await self._write_control_response(
                process,
                self._permission_response(payload["request_id"], request, cached),
            )
            return

        tool_call_id = request.get("tool_use_id") or str(uuid4())
        tool_title = request.get("description") or request.get("display_name") or request.get("tool_name") or "Tool"
        tool_update = update_tool_call(
            tool_call_id,
            title=tool_title,
            kind=tool_kind(request.get("tool_name", "")),
            status="pending",
            raw_input=request.get("input"),
        )
        response = await self.client.request_permission(
            session_id=state.session_id,
            tool_call=tool_update,
            options=[
                PermissionOption(kind="allow_once", name="Allow Once", option_id="allow_once"),
                PermissionOption(kind="allow_always", name="Always Allow", option_id="allow_always"),
                PermissionOption(kind="reject_once", name="Deny Once", option_id="reject_once"),
                PermissionOption(kind="reject_always", name="Always Deny", option_id="reject_always"),
            ],
        )
        selection = self._permission_selection(response)
        if selection in {"allow_always", "reject_always"}:
            state.permission_cache[cache_key] = selection
        await self._write_control_response(
            process,
            self._permission_response(payload["request_id"], request, selection),
        )

    async def _write_control_response(self, process: asyncio.subprocess.Process, payload: dict[str, Any]) -> None:
        if process.stdin is None or process.stdin.is_closing():
            return
        process.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
        await process.stdin.drain()

    def _permission_selection(self, response: RequestPermissionResponse) -> str:
        outcome = response.outcome
        if isinstance(outcome, DeniedOutcome):
            return "reject_once"
        if isinstance(outcome, AllowedOutcome):
            return outcome.option_id
        return "reject_once"

    def _permission_response(self, request_id: str, request: dict[str, Any], selection: str) -> dict[str, Any]:
        if selection in {"allow_once", "allow_always"}:
            classification = "user_permanent" if selection == "allow_always" else "user_temporary"
            response: dict[str, Any] = {
                "behavior": "allow",
                "updatedInput": request.get("input") or {},
                "toolUseID": request.get("tool_use_id"),
                "decisionClassification": classification,
            }
        else:
            response = {
                "behavior": "deny",
                "message": "Permission denied by ACP client",
                "toolUseID": request.get("tool_use_id"),
                "decisionClassification": "user_reject",
            }
        return {
            "type": "control_response",
            "response": {
                "subtype": "success",
                "request_id": request_id,
                "response": response,
            },
        }

    async def _handle_tool_progress(self, session_id: str, payload: dict[str, Any]) -> None:
        await self.client.session_update(
            session_id=session_id,
            update=update_tool_call(
                payload.get("tool_use_id", str(uuid4())),
                title=payload.get("tool_name"),
                kind=tool_kind(payload.get("tool_name", "")),
                status="in_progress",
                raw_output={
                    "elapsed_time_seconds": payload.get("elapsed_time_seconds"),
                    "task_id": payload.get("task_id"),
                },
            ),
        )

    async def _handle_system_message(self, state: SessionState, payload: dict[str, Any]) -> None:
        if payload.get("subtype") == "init":
            state.updated_at = now_iso()

    def _handle_result(self, payload: dict[str, Any]) -> tuple[str, Usage | None]:
        subtype = payload.get("subtype")
        usage_payload = payload.get("usage") or {}
        usage = Usage(
            input_tokens=int(usage_payload.get("input_tokens", 0)),
            output_tokens=int(usage_payload.get("output_tokens", 0)),
            total_tokens=int(usage_payload.get("input_tokens", 0))
            + int(usage_payload.get("output_tokens", 0)),
        )
        if subtype == "error_max_turns":
            return "max_turn_requests", usage
        if subtype == "error_during_execution" and payload.get("is_error"):
            return "end_turn", usage
        return "end_turn", usage

    def _model_state(self, state: SessionState) -> SessionModelState:
        return SessionModelState(
            current_model_id=state.model,
            available_models=[ModelInfo(model_id=state.model, name=state.model)],
        )

    def _mode_state(self, state: SessionState) -> SessionModeState:
        return SessionModeState(
            current_mode_id=state.mode_id,
            available_modes=[
                SessionMode(id=config.mode_id, name=config.name)
                for config in MODE_CONFIGS.values()
            ],
        )


async def main() -> None:
    # JetBrains currently uses ACP session lifecycle/model methods that are
    # still marked unstable by the Python ACP runtime.
    await run_agent(OpenClaudeAgent(), use_unstable_protocol=True)


if __name__ == "__main__":
    asyncio.run(main())
