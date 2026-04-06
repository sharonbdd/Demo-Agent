import { describe, expect, test } from 'bun:test'
import { findToolByName, type Tool, type Tools } from './Tool.js'

describe('findToolByName', () => {
  test('applies shell-tool normalization during lookup', () => {
    const tools = [
      {
        name: 'PowerShell',
        aliases: [],
      },
    ] as Tools

    const originalEnv = process.env.CLAUDE_CODE_USE_POWERSHELL_TOOL
    process.env.CLAUDE_CODE_USE_POWERSHELL_TOOL = '1'

    try {
      const expectedName =
        process.platform === 'win32' ? 'PowerShell' : undefined
      expect(findToolByName(tools, 'Bash')?.name).toBe(expectedName)
    } finally {
      if (originalEnv === undefined) {
        delete process.env.CLAUDE_CODE_USE_POWERSHELL_TOOL
      } else {
        process.env.CLAUDE_CODE_USE_POWERSHELL_TOOL = originalEnv
      }
    }
  })

  test('keeps exact matches unchanged', () => {
    const bashTool = {
      name: 'Bash',
      aliases: [],
    } as Tool

    expect(findToolByName([bashTool] as Tools, 'Bash')).toBe(bashTool)
  })
})
