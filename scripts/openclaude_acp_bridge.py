from __future__ import annotations

import asyncio
import json
import os
import re
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
    update_available_commands,
    update_current_mode,
    update_tool_call,
)
from acp.schema import (
    AgentCapabilities,
    AuthenticateResponse,
    AvailableCommand,
    AvailableCommandInput,
    CloseSessionResponse,
    ConfigOptionUpdate,
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
    SessionConfigOptionSelect,
    SessionConfigSelectOption,
    SessionInfo,
    SessionInfoUpdate,
    SessionListCapabilities,
    SessionMode,
    SessionModeState,
    SessionModelState,
    SessionResumeCapabilities,
    ResumeSessionResponse,
    SetSessionConfigOptionResponse,
    SetSessionModeResponse,
    SetSessionModelResponse,
    UnstructuredCommandInput,
    Usage,
    AllowedOutcome,
    DeniedOutcome,
)


DEBUG = os.environ.get("OPENCLAUDE_ACP_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
}

DEFAULT_PROVIDER = os.environ.get("OPENCLAUDE_MODEL_PROVIDER", "auto").strip().lower()
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "qwen/qwen3.6-plus:free")
DEFAULT_CONTEXT_PROFILE = os.environ.get("OPENCLAUDE_ACP_DEFAULT_CONTEXT_PROFILE", "low").strip().lower()
DEFAULT_WORKFLOW_MODE = os.environ.get("OPENCLAUDE_ACP_DEFAULT_WORKFLOW_MODE", "code").strip().lower()
MODEL_CATALOGS: dict[str, list[str]] = {
    "openrouter": [
        "qwen/qwen3.6-plus:free",
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-chat",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
    ],
    "huggingface": [
        "Qwen/Qwen3-Coder-Next-FP8:together",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "google/gemma-2-27b-it",
    ],
    "local_openai": [
        "gpt-4o-mini",
        "deepseek-chat",
        "llama3.3:70b",
        "qwen2.5-coder:7b",
    ],
    "ollama": [
        "llama3.3:70b",
        "qwen2.5-coder:7b",
        "llama3.1:8b",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
    ],
}
READ_ONLY_TOOLS = {
    "Read",
    "Glob",
    "Grep",
    "WebFetch",
    "WebSearch",
    "ListMcpResourcesTool",
    "ReadMcpResource",
    "ToolSearch",
}
PLAN_MARKDOWN_TOOLS = {"Write", "Edit"}
MUTATING_TOOLS = {
    "Write",
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "TodoWrite",
    "Bash",
    "PowerShell",
}
WORKFLOW_MODES = ("ask", "plan", "fix", "code")
CONTEXT_PROFILES = ("low", "high")
SESSION_COMMANDS: tuple[tuple[str, str], ...] = (
    ("/low", "Switch to LOW context profile (32k-oriented)."),
    ("/high", "Switch to HIGH context profile (128k-oriented)."),
    ("/ask", "Switch to ASK workflow mode (consultative, no edits)."),
    ("/plan", "Switch to PLAN workflow mode (Markdown-only planning)."),
    ("/fix", "Switch to FIX workflow mode (testing and bounded repairs)."),
    ("/code", "Switch to CODE workflow mode (implementation mode)."),
    ("/brave", "Bypass ACP confirmations while keeping workflow restrictions intact."),
    ("/careful", "Require ACP confirmations for mutating actions."),
)
PREVIEW_LIMIT = 120
STDERR_TAIL_LIMIT = 12


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
        if (candidate / "package.json").exists() and (candidate / "bin").exists():
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
    launcher_name = "openclaude-openrouter.cmd" if sys.platform == "win32" else "openclaude"
    return repo_root() / "bin" / launcher_name


def runtime_platform() -> str:
    return "windows" if sys.platform == "win32" else "linux"


def preferred_shell_tool() -> str:
    return "PowerShell" if runtime_platform() == "windows" else "Bash"


def state_path() -> Path:
    override = os.environ.get("OPENCLAUDE_ACP_STATE_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / ".openclaude-acp-sessions.json"


def _parse_csv_env(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def detect_provider() -> str:
    provider = DEFAULT_PROVIDER
    if provider and provider != "auto":
        return provider

    base_url = os.environ.get("OPENAI_BASE_URL", "").strip().lower()
    launcher_name = launcher_path().name.lower()
    if "huggingface.co" in base_url:
        return "huggingface"
    if "openrouter.ai" in base_url or "openrouter" in launcher_name:
        return "openrouter"
    if "localhost" in base_url or "127.0.0.1" in base_url:
        if "11434" in base_url or "ollama" in launcher_name:
            return "ollama"
        return "local_openai"
    if "api.openai.com" in base_url:
        return "openai"
    return "openrouter"


def available_models() -> list[str]:
    provider = detect_provider()
    catalog = list(MODEL_CATALOGS.get(provider, MODEL_CATALOGS["openrouter"]))
    catalog.extend(_parse_csv_env("OPENCLAUDE_EXTRA_MODELS"))

    explicit_models = _parse_csv_env("OPENCLAUDE_ACP_MODELS")
    if explicit_models:
        catalog = explicit_models + [model for model in catalog if model not in explicit_models]

    ordered: list[str] = []
    for model in catalog:
        if model not in ordered:
            ordered.append(model)
    return ordered


def normalize_context_profile(value: str | None) -> str:
    value = (value or DEFAULT_CONTEXT_PROFILE).strip().lower()
    return value if value in CONTEXT_PROFILES else "low"


def normalize_workflow_mode(value: str | None) -> str:
    value = (value or DEFAULT_WORKFLOW_MODE).strip().lower()
    return value if value in WORKFLOW_MODES else "code"


def normalize_brave_mode(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "on", "brave"}


def parse_mode_id(mode_id: str, current_context_profile: str | None = None) -> tuple[str, str] | None:
    normalized = mode_id.strip().lower()
    if normalized in WORKFLOW_MODES:
        return normalize_context_profile(current_context_profile), normalized
    if "_" in normalized:
        context_profile, workflow_mode = normalized.split("_", 1)
        if context_profile in CONTEXT_PROFILES and workflow_mode in WORKFLOW_MODES:
            return context_profile, workflow_mode
    return None


def serialize_input(payload: dict[str, Any]) -> str:
    try:
        return json.dumps(payload, sort_keys=True, default=str)
    except TypeError:
        return repr(payload)


def is_mutating_tool(tool_name: str) -> bool:
    return tool_name in MUTATING_TOOLS


def _truncate_preview(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    if len(text) <= PREVIEW_LIMIT:
        return text
    return f"{text[: PREVIEW_LIMIT - 3]}..."


def change_preview(tool_name: str, input_payload: dict[str, Any]) -> str | None:
    target = input_payload.get("file_path") or input_payload.get("path")
    command = input_payload.get("command")
    if tool_name in {"Write", "Edit", "MultiEdit", "NotebookEdit", "TodoWrite"} and target:
        pieces = [f"path={target}"]
        for key in ("old_string", "new_string", "content", "text", "instruction"):
            value = input_payload.get(key)
            if value:
                pieces.append(f"{key}={_truncate_preview(value)}")
                break
        return " | ".join(pieces)
    if tool_name in {"Bash", "PowerShell"} and command:
        return f"command={_truncate_preview(command)}"
    return f"path={target}" if target else None


def permission_prompt_title(tool_name: str, input_payload: dict[str, Any], workflow_mode: str) -> str:
    preview = change_preview(tool_name, input_payload)
    role_prefix = workflow_mode.upper()
    if preview:
        return f"{role_prefix}: {tool_name} -> {preview}"
    return f"{role_prefix}: {tool_name}"


def summarize_stderr_tail(stderr_lines: list[str]) -> str:
    if not stderr_lines:
        return "No stderr output was captured."
    tail = stderr_lines[-STDERR_TAIL_LIMIT:]
    return "\n".join(f"- {line}" for line in tail)


def normalize_provider_auth_env(env: dict[str, str]) -> None:
    provider = env.get("OPENCLAUDE_MODEL_PROVIDER", "").strip().lower()
    if provider == "huggingface" and not env.get("OPENAI_API_KEY") and env.get("HF_TOKEN"):
        env["OPENAI_API_KEY"] = env["HF_TOKEN"]
    if provider == "openrouter" and not env.get("OPENAI_API_KEY") and env.get("OPEN_ROUTER_KEY"):
        env["OPENAI_API_KEY"] = env["OPEN_ROUTER_KEY"]


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


def build_session_commands() -> list[AvailableCommand]:
    commands: list[AvailableCommand] = []
    for command_name, description in SESSION_COMMANDS:
        commands.append(
            AvailableCommand(
                name=command_name[1:],
                description=description,
                input=AvailableCommandInput(
                    root=UnstructuredCommandInput(hint="optional follow-up prompt"),
                ),
            )
        )
    return commands


def build_config_options(current_model: str, context_profile: str, workflow_mode: str, brave: bool) -> list[SessionConfigOptionSelect]:
    model_options = [
        SessionConfigSelectOption(
            value=model_id,
            name=model_id,
            description=f"Use {model_id}",
        )
        for model_id in available_models()
    ]
    if current_model not in {option.value for option in model_options}:
        model_options.insert(
            0,
            SessionConfigSelectOption(
                value=current_model,
                name=current_model,
                description="Current session model",
            ),
        )

    return [
        SessionConfigOptionSelect(
            id="context_profile",
            name="Context Profile",
            description="LOW is 32k-oriented; HIGH is 128k-oriented.",
            category="thought_level",
            type="select",
            currentValue=context_profile,
            options=[
                SessionConfigSelectOption(
                    value="low",
                    name="LOW",
                    description="Smaller context budget, earlier compaction, concise planning.",
                ),
                SessionConfigSelectOption(
                    value="high",
                    name="HIGH",
                    description="Larger context budget, richer replay, deeper planning and verification.",
                ),
            ],
        ),
        SessionConfigOptionSelect(
            id="workflow_mode",
            name="Workflow Mode",
            description="Controls editing policy, tool access, and expected engineering role.",
            category="mode",
            type="select",
            currentValue=workflow_mode,
            options=[
                SessionConfigSelectOption(value="ask", name="ASK", description="Consultant/specification mode. No edits allowed."),
                SessionConfigSelectOption(value="plan", name="PLAN", description="Architect mode. Markdown-only planning edits."),
                SessionConfigSelectOption(value="fix", name="FIX", description="Testing/debugging mode with bounded repair work."),
                SessionConfigSelectOption(value="code", name="CODE", description="Implementation mode with full coding workflow."),
            ],
        ),
        SessionConfigOptionSelect(
            id="model",
            name="Model",
            description="Select the current provider model for this ACP session.",
            category="model",
            type="select",
            currentValue=current_model,
            options=model_options,
        ),
        SessionConfigOptionSelect(
            id="brave_mode",
            name="Brave Mode",
            description="OFF asks for ACP confirmations before mutating actions in FIX/CODE. ON bypasses confirmations but keeps workflow restrictions.",
            category="permissions",
            type="select",
            currentValue="on" if brave else "off",
            options=[
                SessionConfigSelectOption(
                    value="off",
                    name="OFF",
                    description="Default. Require ACP confirmations for mutating actions.",
                ),
                SessionConfigSelectOption(
                    value="on",
                    name="ON",
                    description="Brave. Bypass ACP confirmation prompts while preserving workflow tool restrictions.",
                ),
            ],
        ),
    ]


def workflow_instruction(state: SessionState) -> str:
    shell_guidance = {
        "windows": (
            "Platform: Windows. Prefer the PowerShell tool for terminal work. "
            "Do not assume Bash is the primary interactive shell on this machine."
        ),
        "linux": (
            "Platform: Linux. Prefer the Bash tool for terminal work."
        ),
    }[runtime_platform()]
    profile_instruction = {
        "low": (
            "Use a LOW context-budget operating profile. Be concise, avoid unnecessary transcript expansion, "
            "and prefer smaller verification scopes unless the user explicitly asks for depth."
        ),
        "high": (
            "Use a HIGH context-budget operating profile. You may retain more context, provide fuller plans, "
            "and perform deeper verification when justified."
        ),
    }[state.context_profile]
    workflow_policy = {
        "ask": (
            "You are in ASK workflow mode. Act as a consultant/specification elicitor. "
            "Do not modify files, do not run write-capable shell commands, and do not make code or document edits."
        ),
        "plan": (
            "You are in PLAN workflow mode. Act as a manager/systems architect. "
            "Do not edit source code. You may only create, update, or append Markdown files for planning artifacts."
        ),
        "fix": (
            "You are in FIX workflow mode. Act as a tester/debugger. Prioritize testing, diagnosis, and bounded repairs. "
            "If a fix would require substantial changes, defer it to later iterations and document the deferred work. "
            + (
                "Brave mode is ON, so ACP confirmations may be bypassed."
                if state.brave
                else "Brave mode is OFF, so mutating actions should be confirmation-first."
            )
        ),
        "code": (
            "You are in CODE workflow mode. Act as a software developer. "
            "Implement requested changes directly and report all modifications transparently. "
            + (
                "Brave mode is ON, so ACP confirmations may be bypassed."
                if state.brave
                else "Brave mode is OFF, so mutating actions should be confirmation-first."
            )
        ),
    }[state.workflow_mode]
    return f"[ACP session policy]\n{shell_guidance}\n{profile_instruction}\n{workflow_policy}"


def apply_session_command(state: SessionState, user_text: str) -> tuple[bool, str]:
    stripped = user_text.strip()
    if not stripped.startswith("/"):
        return False, user_text

    parts = stripped.split(maxsplit=1)
    command = parts[0].lower()
    remainder = parts[1] if len(parts) > 1 else ""
    if command in {"/low", "/high"}:
        state.context_profile = command[1:]
        return True, remainder
    if command in {"/ask", "/plan", "/fix", "/code"}:
        state.workflow_mode = command[1:]
        return True, remainder
    if command == "/brave":
        state.brave = True
        return True, remainder
    if command in {"/careful", "/confirm"}:
        state.brave = False
        return True, remainder
    parsed = parse_mode_id(command[1:].replace("-", "_"), state.context_profile)
    if parsed:
        state.context_profile, state.workflow_mode = parsed
        return True, remainder
    return False, user_text


def is_markdown_path(input_payload: dict[str, Any]) -> bool:
    for key in ("file_path", "path"):
        value = input_payload.get(key)
        if isinstance(value, str):
            return value.lower().endswith(".md")
    return False


def is_tool_allowed_for_workflow(tool_name: str, input_payload: dict[str, Any], workflow_mode: str) -> bool:
    if workflow_mode == "ask":
        return tool_name in READ_ONLY_TOOLS or tool_name == "AskUserQuestion"
    if workflow_mode == "plan":
        if tool_name in READ_ONLY_TOOLS or tool_name in {"AskUserQuestion", "TodoWrite"}:
            return True
        if tool_name in PLAN_MARKDOWN_TOOLS:
            return is_markdown_path(input_payload)
        return False
    return True


def should_disable_slash_commands(workflow_mode: str) -> bool:
    return workflow_mode in {"ask", "plan"}


def tools_arg_for_workflow(workflow_mode: str) -> str | None:
    if workflow_mode == "ask":
        return ",".join(sorted(READ_ONLY_TOOLS | {"AskUserQuestion"}))
    if workflow_mode == "plan":
        return ",".join(sorted(READ_ONLY_TOOLS | PLAN_MARKDOWN_TOOLS | {"AskUserQuestion", "TodoWrite"}))
    return None


def derive_title(user_text: str) -> str | None:
    stripped = re.sub(r"\s+", " ", user_text).strip(" -:\n\t")
    if not stripped or stripped.startswith("/"):
        return None
    return stripped[:72]


@dataclass
class SessionState:
    session_id: str
    cwd: str
    model: str = DEFAULT_MODEL
    context_profile: str = field(default_factory=lambda: normalize_context_profile(DEFAULT_CONTEXT_PROFILE))
    workflow_mode: str = field(default_factory=lambda: normalize_workflow_mode(DEFAULT_WORKFLOW_MODE))
    brave: bool = field(default_factory=lambda: normalize_brave_mode(os.environ.get("OPENCLAUDE_ACP_DEFAULT_BRAVE")))
    title: str | None = None
    updated_at: str = field(default_factory=now_iso)
    has_started: bool = False
    permission_cache: dict[str, str] = field(default_factory=dict)
    active_process: asyncio.subprocess.Process | None = None

    @property
    def mode_id(self) -> str:
        return self.workflow_mode

    def to_json(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "cwd": self.cwd,
            "model": self.model,
            "context_profile": self.context_profile,
            "workflow_mode": self.workflow_mode,
            "brave": self.brave,
            "title": self.title,
            "updated_at": self.updated_at,
            "has_started": self.has_started,
            "permission_cache": dict(self.permission_cache),
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> SessionState:
        return cls(
            session_id=payload["session_id"],
            cwd=payload["cwd"],
            model=payload.get("model", DEFAULT_MODEL),
            context_profile=normalize_context_profile(payload.get("context_profile")),
            workflow_mode=normalize_workflow_mode(payload.get("workflow_mode")),
            brave=normalize_brave_mode(payload.get("brave")),
            title=payload.get("title"),
            updated_at=payload.get("updated_at", now_iso()),
            has_started=bool(payload.get("has_started", False)),
            permission_cache=dict(payload.get("permission_cache") or {}),
        )


class OpenClaudeAgent:
    def __init__(self) -> None:
        self.client = None
        self.sessions: dict[str, SessionState] = {}
        self._load_sessions()

    def on_connect(self, conn) -> None:
        self.client = conn

    def _load_sessions(self) -> None:
        path = state_path()
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            log(f"failed to read persisted sessions: {exc}")
            return
        for raw_state in payload.get("sessions", []):
            try:
                state = SessionState.from_json(raw_state)
                self.sessions[state.session_id] = state
            except Exception as exc:
                log(f"failed to hydrate session: {exc}")

    def _save_sessions(self) -> None:
        path = state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "updated_at": now_iso(),
            "sessions": [state.to_json() for state in self.sessions.values()],
        }
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp_path.replace(path)

    def _persist_state(self, state: SessionState) -> None:
        self.sessions[state.session_id] = state
        self._save_sessions()

    def _config_options(self, state: SessionState) -> list[SessionConfigOptionSelect]:
        return build_config_options(state.model, state.context_profile, state.workflow_mode, state.brave)

    async def _notify_session_controls(self, state: SessionState) -> None:
        if self.client is None:
            return
        await self.client.session_update(
            session_id=state.session_id,
            update=update_available_commands(build_session_commands()),
        )
        await self.client.session_update(
            session_id=state.session_id,
            update=update_current_mode(state.mode_id),
        )
        await self.client.session_update(
            session_id=state.session_id,
            update=ConfigOptionUpdate(
                sessionUpdate="config_option_update",
                configOptions=self._config_options(state),
            ),
        )

    async def _notify_session_info(self, state: SessionState) -> None:
        if self.client is None:
            return
        await self.client.session_update(
            session_id=state.session_id,
            update=SessionInfoUpdate(
                sessionUpdate="session_info_update",
                title=state.title,
                updatedAt=state.updated_at,
            ),
        )

    async def _send_final_message(self, session_id: str, text: str) -> None:
        if self.client is None:
            return
        await self.client.session_update(
            session_id=session_id,
            update=update_agent_message(text_block(text)),
        )

    async def _error_prompt_response(
        self,
        session_id: str,
        message_id: str | None,
        text: str,
    ) -> PromptResponse:
        await self._send_final_message(session_id, text)
        return PromptResponse(
            stop_reason="end_turn",
            usage=Usage(input_tokens=0, output_tokens=0, total_tokens=0),
            user_message_id=message_id,
        )

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
                name="openclaude-acp",
                title="OpenClaude ACP",
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
        self._persist_state(state)
        log(f"new_session({cwd}) -> {session_id}")
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return NewSessionResponse(
            session_id=session_id,
            modes=self._mode_state(state),
            models=self._model_state(state),
            config_options=self._config_options(state),
        )

    def _get_or_create_session(self, cwd: str, session_id: str) -> SessionState:
        state = self.sessions.get(session_id)
        if state is None:
            state = SessionState(
                session_id=session_id,
                cwd=cwd,
                title=Path(cwd).name or cwd,
                has_started=True,
            )
        state.cwd = cwd
        state.updated_at = now_iso()
        self._persist_state(state)
        return state

    async def load_session(self, cwd: str, session_id: str, mcp_servers=None, **kwargs: Any) -> LoadSessionResponse:
        state = self._get_or_create_session(cwd, session_id)
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return LoadSessionResponse(
            modes=self._mode_state(state),
            models=self._model_state(state),
            config_options=self._config_options(state),
        )

    async def resume_session(self, cwd: str, session_id: str, mcp_servers=None, **kwargs: Any) -> ResumeSessionResponse:
        state = self._get_or_create_session(cwd, session_id)
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return ResumeSessionResponse(
            modes=self._mode_state(state),
            models=self._model_state(state),
            config_options=self._config_options(state),
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
        parsed = parse_mode_id(mode_id, state.context_profile)
        if parsed is None:
            return None
        state.context_profile, state.workflow_mode = parsed
        state.updated_at = now_iso()
        self._persist_state(state)
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return SetSessionModeResponse()

    async def set_session_model(self, model_id: str, session_id: str, **kwargs: Any):
        state = self.sessions.get(session_id)
        if state is None:
            return None
        state.model = model_id
        state.updated_at = now_iso()
        self._persist_state(state)
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return SetSessionModelResponse()

    async def set_config_option(self, config_id: str, session_id: str, value: str | bool, **kwargs: Any):
        state = self.sessions.get(session_id)
        if state is None:
            return None
        string_value = str(value).strip().lower()
        if config_id == "context_profile":
            state.context_profile = normalize_context_profile(string_value)
        elif config_id == "workflow_mode":
            state.workflow_mode = normalize_workflow_mode(string_value)
        elif config_id == "brave_mode":
            state.brave = normalize_brave_mode(value)
        elif config_id == "model":
            state.model = str(value)
        else:
            return None
        state.updated_at = now_iso()
        self._persist_state(state)
        await self._notify_session_controls(state)
        await self._notify_session_info(state)
        return SetSessionConfigOptionResponse(config_options=self._config_options(state))

    async def authenticate(self, method_id: str, **kwargs: Any):
        return AuthenticateResponse()

    async def close_session(self, session_id: str, **kwargs: Any):
        state = self.sessions.get(session_id)
        if state and state.active_process and state.active_process.returncode is None:
            state.active_process.terminate()
            await state.active_process.wait()
        if state:
            state.active_process = None
            state.updated_at = now_iso()
            self._persist_state(state)
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
            return await self._error_prompt_response(
                session_id,
                message_id,
                f"I could not continue because ACP session `{session_id}` was not found. "
                "Create or reload the session and retry the request.",
            )

        user_text = extract_text_from_prompt(prompt)
        if not user_text:
            user_text = "[empty prompt]"

        session_command_applied, remainder = apply_session_command(state, user_text)
        if session_command_applied:
            state.updated_at = now_iso()
            self._persist_state(state)
            await self._notify_session_controls(state)
            await self._notify_session_info(state)
            if remainder.strip():
                user_text = remainder.strip()
            else:
                await self.client.session_update(
                    session_id=session_id,
                    update=update_agent_message(
                        text_block(
                            f"Session updated: profile={state.context_profile.upper()}, "
                            f"workflow={state.workflow_mode.upper()}, model={state.model}, "
                            f"brave={'ON' if state.brave else 'OFF'}"
                        )
                    ),
                )
                return PromptResponse(
                    stop_reason="end_turn",
                    usage=Usage(input_tokens=0, output_tokens=0, total_tokens=0),
                    user_message_id=message_id,
                )

        title = derive_title(user_text)
        if title and not state.has_started and state.title != title:
            state.title = title
            state.updated_at = now_iso()
            self._persist_state(state)
            await self._notify_session_info(state)

        user_text = f"{workflow_instruction(state)}\n\n{user_text}"
        command = self._build_command(state, new_session=not state.has_started)

        env = os.environ.copy()
        env["OPENAI_MODEL"] = state.model
        env["OPENCLAUDE_ACP_CONTEXT_PROFILE"] = state.context_profile
        env["OPENCLAUDE_ACP_WORKFLOW_MODE"] = state.workflow_mode
        env["OPENCLAUDE_ACP_BRAVE"] = "1" if state.brave else "0"
        env["OPENCLAUDE_ACP_PLATFORM"] = runtime_platform()
        env["CLAUDE_CODE_USE_POWERSHELL_TOOL"] = "1" if runtime_platform() == "windows" else "0"
        normalize_provider_auth_env(env)

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=state.cwd,
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as exc:
            return await self._error_prompt_response(
                session_id,
                message_id,
                f"I had to stop before starting the runtime. Launch failed for platform `{runtime_platform()}` "
                f"using launcher `{launcher_path()}`. Reason: {exc}",
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

        stderr_lines: list[str] = []
        stderr_task = asyncio.create_task(self._drain_stderr(process, stderr_lines))
        stop_reason = "end_turn"
        usage = Usage(input_tokens=0, output_tokens=0, total_tokens=0)
        child_result_seen = False
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
                    child_result_seen = True
                    stop_reason, usage = self._handle_result(payload)
                elif payload_type == "system":
                    await self._handle_system_message(state, payload)
            returncode = await process.wait()
            await stderr_task
            if returncode != 0:
                detail = summarize_stderr_tail(stderr_lines)
                return await self._error_prompt_response(
                    session_id,
                    message_id,
                    "I had to stop because the OpenClaude runtime exited early.\n"
                    f"Exit code: {returncode}\n"
                    f"Platform: {runtime_platform()}\n"
                    f"Preferred shell: {preferred_shell_tool()}\n"
                    f"Recent stderr:\n{detail}",
                )
            if not child_result_seen:
                detail = summarize_stderr_tail(stderr_lines)
                return await self._error_prompt_response(
                    session_id,
                    message_id,
                    "I had to stop because the runtime ended without producing a final result.\n"
                    f"Platform: {runtime_platform()}\n"
                    f"Preferred shell: {preferred_shell_tool()}\n"
                    f"Recent stderr:\n{detail}",
                )
            state.has_started = True
        except Exception as exc:
            detail = summarize_stderr_tail(stderr_lines)
            return await self._error_prompt_response(
                session_id,
                message_id,
                "I had to stop because an unexpected bridge/runtime error occurred.\n"
                f"Reason: {exc}\n"
                f"Platform: {runtime_platform()}\n"
                f"Preferred shell: {preferred_shell_tool()}\n"
                f"Recent stderr:\n{detail}",
            )
        finally:
            state.active_process = None
            state.updated_at = now_iso()
            self._persist_state(state)
            await self._notify_session_info(state)

        return PromptResponse(
            stop_reason=stop_reason,
            usage=usage,
            user_message_id=message_id,
        )

    def _build_command(self, state: SessionState, *, new_session: bool) -> list[str]:
        launcher = launcher_path()
        if not launcher.exists():
            raise FileNotFoundError(f"Launcher not found: {launcher}")

        args = [str(launcher), "-p", "--verbose", "--input-format", "stream-json", "--output-format", "stream-json"]
        if runtime_platform() == "windows":
            args = ["cmd.exe", "/d", "/c", *args]
        workflow_tools = tools_arg_for_workflow(state.workflow_mode)
        if workflow_tools is not None:
            args.extend(["--tools", workflow_tools])
        if should_disable_slash_commands(state.workflow_mode):
            args.append("--disable-slash-commands")
        if new_session:
            args.extend(["--session-id", state.session_id])
        else:
            args.extend(["--resume", state.session_id])
        return args

    async def _drain_stderr(self, process: asyncio.subprocess.Process, sink: list[str]) -> None:
        if process.stderr is None:
            return
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if text:
                sink.append(text)
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

        request_input = request.get("input") or {}
        tool_name = request.get("tool_name", "")
        if not is_tool_allowed_for_workflow(tool_name, request_input, state.workflow_mode):
            await self._write_control_response(
                process,
                self._permission_response(
                    payload["request_id"],
                    request,
                    "reject_once",
                    deny_message=f"Tool {tool_name} is not allowed in {state.workflow_mode.upper()} workflow mode.",
                ),
            )
            return

        if state.brave:
            await self._write_control_response(
                process,
                self._permission_response(payload["request_id"], request, "allow_once"),
            )
            return

        cache_key = f"{tool_name}::{serialize_input(request_input)}"
        cached = state.permission_cache.get(cache_key)
        if cached is not None:
            await self._write_control_response(
                process,
                self._permission_response(payload["request_id"], request, cached),
            )
            return

        tool_call_id = request.get("tool_use_id") or str(uuid4())
        tool_title = request.get("description") or request.get("display_name") or permission_prompt_title(
            tool_name, request_input, state.workflow_mode
        )
        tool_update = update_tool_call(
            tool_call_id,
            title=tool_title,
            kind=tool_kind(tool_name),
            status="pending",
            raw_input=request_input,
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
            self._persist_state(state)
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

    def _permission_response(
        self,
        request_id: str,
        request: dict[str, Any],
        selection: str,
        *,
        deny_message: str = "Permission denied by ACP client",
    ) -> dict[str, Any]:
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
                "message": deny_message,
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
            self._persist_state(state)

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
        models_list = available_models()
        models = [ModelInfo(model_id=m, name=m) for m in models_list]
        if state.model not in models_list:
            models.insert(0, ModelInfo(model_id=state.model, name=state.model))

        return SessionModelState(
            current_model_id=state.model,
            available_models=models,
        )

    def _mode_state(self, state: SessionState) -> SessionModeState:
        available_modes = [
            SessionMode(
                id=workflow_mode,
                name=workflow_mode.upper(),
                description={
                    "ask": "Consultant/specification mode. No file edits.",
                    "plan": "Architect/planning mode. Markdown-only planning edits.",
                    "fix": "Testing/debugging mode with bounded repair work.",
                    "code": "Implementation mode for code and documentation changes.",
                }[workflow_mode],
            )
            for workflow_mode in WORKFLOW_MODES
        ]
        return SessionModeState(
            current_mode_id=state.mode_id,
            available_modes=available_modes,
        )


async def main() -> None:
    # JetBrains currently uses ACP session lifecycle/model methods that are
    # still marked unstable by the Python ACP runtime.
    await run_agent(OpenClaudeAgent(), use_unstable_protocol=True)


if __name__ == "__main__":
    asyncio.run(main())
