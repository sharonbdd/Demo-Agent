@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"

if defined OPENCLAUDE_BUN_PATH (
  set "BUN_EXE=%OPENCLAUDE_BUN_PATH%"
) else (
  set "BUN_EXE=C:\Users\Sharon Boddu\AppData\Local\Microsoft\WinGet\Packages\Oven-sh.Bun_Microsoft.Winget.Source_8wekyb3d8bbwe\bun-windows-x64\bun.exe"
)

if not exist "%BUN_EXE%" (
  echo Bun executable not found: "%BUN_EXE%"
  exit /b 1
)

if not defined OPENAI_API_KEY if defined OPEN_ROUTER_KEY set "OPENAI_API_KEY=%OPEN_ROUTER_KEY%"
if not defined OPENAI_API_KEY if defined OPENROUTER_API_KEY set "OPENAI_API_KEY=%OPENROUTER_API_KEY%"

if not defined CLAUDE_CODE_USE_OPENAI set "CLAUDE_CODE_USE_OPENAI=1"
if not defined OPENAI_BASE_URL set "OPENAI_BASE_URL=https://openrouter.ai/api/v1"
if not defined OPENAI_MODEL set "OPENAI_MODEL=qwen/qwen3.6-plus:free"

if not defined OPENAI_API_KEY (
  echo Missing OpenRouter API key. Set OPEN_ROUTER_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY before launching OpenClaude.
  exit /b 1
)

"%BUN_EXE%" "%REPO_ROOT%\dist\cli.mjs" %*
