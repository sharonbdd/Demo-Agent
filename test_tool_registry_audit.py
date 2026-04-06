import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def run_bun_tool_dump(extra_env: dict[str, str] | None = None) -> list[dict[str, object]]:
    env = os.environ.copy()
    env["CLAUDE_CODE_USE_OPENAI"] = "1"
    env["OPENAI_MODEL"] = "gpt-4o-mini"
    if extra_env:
        env.update(extra_env)

    command = [
        "bun",
        "-e",
        (
            "const cfg = await import('./src/utils/config.ts'); "
            "cfg.enableConfigs(); "
            "const mod = await import('./src/tools.ts'); "
            "const tools = mod.getAllBaseTools().map(t => ({name: t.name, enabled: t.isEnabled()})); "
            "console.log(JSON.stringify(tools));"
        ),
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_default_open_build_tool_registry_matches_expected_surface():
    tools = run_bun_tool_dump()
    names = {tool["name"] for tool in tools}

    assert {
        "Agent",
        "Bash",
        "Read",
        "Edit",
        "Write",
        "Glob",
        "Grep",
        "WebFetch",
        "WebSearch",
        "AskUserQuestion",
        "Skill",
        "EnterWorktree",
        "ExitWorktree",
        "ListMcpResourcesTool",
        "ReadMcpResourceTool",
        "ToolSearch",
    }.issubset(names)
    assert "PowerShell" not in names
    assert "TaskCreate" not in names


def test_env_gated_open_repo_tools_are_registered_when_enabled():
    tools = run_bun_tool_dump(
        {
            "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1",
            "CLAUDE_CODE_ENABLE_TASKS": "1",
            "ENABLE_LSP_TOOL": "1",
            "CLAUDE_CODE_VERIFY_PLAN": "true",
            "NODE_ENV": "test",
        }
    )
    tool_map = {tool["name"]: bool(tool["enabled"]) for tool in tools}

    assert "PowerShell" in tool_map
    assert "TaskCreate" in tool_map
    assert "TaskGet" in tool_map
    assert "TaskUpdate" in tool_map
    assert "TaskList" in tool_map
    assert "LSP" in tool_map
    assert "TestingPermission" in tool_map


def test_tools_inventory_file_covers_well_over_fifty_capabilities():
    payload = json.loads((REPO_ROOT / "tools.json").read_text(encoding="utf-8"))
    total = sum(
        len(payload[key])
        for key in (
            "core_tools",
            "task_and_worktree_tools",
            "optional_or_feature_gated_tools",
            "dynamic_tools",
        )
    )
    assert total >= 50


def test_checked_in_acp_configs_keep_idea_mcp_enabled():
    acp_json = REPO_ROOT / "ACP" / "ACP-JSONS" / "agent.json"
    payload = json.loads(acp_json.read_text(encoding="utf-8"))
    settings = payload["default_mcp_settings"]

    assert settings["use_custom_mcp"] is True
    assert settings["use_idea_mcp"] is True
    assert "idea_mcp_allowed_tools" in settings
    assert {
        "get_project_modules",
        "open_file_in_editor",
        "find_files_by_name",
        "execute_terminal_command",
        "rename_refactoring",
        "get_symbol_info",
        "search_in_files_by_text",
    }.issubset(set(settings["idea_mcp_allowed_tools"]))
