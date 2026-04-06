# Agent-ACP Verification Matrix

Use this matrix before broad ACP tool testing.

## Session Control
- [ ] `context_profile=low` updates the ACP config option state.
- [ ] `context_profile=high` updates the ACP config option state.
- [ ] `workflow_mode=ask` updates the ACP config option state.
- [ ] `workflow_mode=plan` updates the ACP config option state.
- [ ] `workflow_mode=fix` updates the ACP config option state.
- [ ] `workflow_mode=code` updates the ACP config option state.
- [ ] ACP mode selection exposes only `ask`, `plan`, `fix`, and `code`.
- [ ] ACP mode selection stays synchronized with the `workflow_mode` config option.
- [ ] Legacy combined mode IDs still parse correctly if restored from older state.
- [ ] Slash commands stay synchronized with config options and ACP modes.

## Workflow Policy
- [ ] ASK denies all edits and write-capable shell activity.
- [ ] PLAN only allows Markdown planning edits.
- [ ] FIX permits testing and bounded repairs.
- [ ] CODE permits standard implementation workflows.

## Persistence
- [ ] `session/list` survives bridge restart.
- [ ] `session/load` restores model, context profile, workflow mode, title, and transcript linkage.
- [ ] Session titles and timestamps update in the ACP client.

## UX Parity
- [ ] Available slash commands are advertised in the ACP client.
- [ ] Mode/config updates appear immediately after changes.
- [ ] Permission prompts still work after workflow gating.
- [ ] Tool progress continues streaming during long-running actions.

## Provider Coverage
- [ ] Generic `agent.json` preset launches correctly from `openclaude-acp-low.exe`.
- [ ] OpenRouter LOW
- [ ] OpenRouter HIGH
- [ ] OpenAI LOW
- [ ] OpenAI HIGH
- [ ] HuggingFace LOW
- [ ] HuggingFace HIGH
- [ ] Local OpenAI LOW
- [ ] Local OpenAI HIGH
- [ ] Ollama LOW
- [ ] Ollama HIGH
