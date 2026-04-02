from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
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
        return find_repo_root(Path(sys.executable).resolve().parent)
    return find_repo_root(Path(__file__).resolve().parent)


def launcher_path() -> Path:
    override = os.environ.get("OPENCLAUDE_LAUNCHER", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / "bin" / "openclaude-openrouter.cmd"


def main() -> int:
    launcher = launcher_path()
    if not launcher.exists():
        print(f"Launcher not found: {launcher}", file=sys.stderr)
        return 1

    command = ["cmd.exe", "/d", "/c", str(launcher), *sys.argv[1:]]
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
