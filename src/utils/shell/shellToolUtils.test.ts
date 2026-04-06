import { describe, expect, test } from 'bun:test'
import { BASH_TOOL_NAME } from '../../tools/BashTool/toolName.js'
import { POWERSHELL_TOOL_NAME } from '../../tools/PowerShellTool/toolName.js'
import {
  getPreferredShellToolName,
  normalizeShellToolName,
} from './shellToolUtils.js'

describe('shellToolUtils', () => {
  test('remaps Bash to PowerShell on Windows when PowerShell is enabled', () => {
    expect(normalizeShellToolName(BASH_TOOL_NAME, 'windows', true)).toBe(
      POWERSHELL_TOOL_NAME,
    )
  })

  test('keeps Bash on Windows when PowerShell is disabled', () => {
    expect(normalizeShellToolName(BASH_TOOL_NAME, 'windows', false)).toBe(
      BASH_TOOL_NAME,
    )
  })

  test('keeps Bash on non-Windows platforms', () => {
    expect(normalizeShellToolName(BASH_TOOL_NAME, 'linux', true)).toBe(
      BASH_TOOL_NAME,
    )
  })

  test('returns the preferred shell tool name for the current platform state', () => {
    expect(getPreferredShellToolName('windows', true)).toBe(
      POWERSHELL_TOOL_NAME,
    )
    expect(getPreferredShellToolName('linux', true)).toBe(BASH_TOOL_NAME)
  })
})
