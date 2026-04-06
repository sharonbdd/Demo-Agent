import { describe, expect, test } from 'bun:test'
import {
  convertAssistantTextToolCallFallback,
  normalizeParsedToolCall,
  parseXmlStyleToolCall,
} from './toolCallFallback.js'
import { getPlatform } from './platform.js'

describe('toolCallFallback', () => {
  test('parses xml-style function markup into tool call input', () => {
    const parsed = parseXmlStyleToolCall(`
      <tool_call>
        <function=Bash>
          <parameter=command>ls -la "F:/PyCharm/Speaker"</parameter>
        </function>
      </tool_call>
    `)

    expect(parsed).not.toBeNull()
    expect(parsed?.name).toBe('Bash')
    expect(parsed?.input.command).toBe('ls -la "F:/PyCharm/Speaker"')
  })

  test('converts assistant text-only tool markup into tool_use content', () => {
    const message = {
      type: 'assistant',
      uuid: 'u1',
      timestamp: '2026-04-06T00:00:00Z',
      message: {
        id: 'm1',
        type: 'message',
        role: 'assistant',
        model: 'test-model',
        stop_reason: 'end_turn',
        stop_sequence: null,
        usage: {
          input_tokens: 0,
          output_tokens: 0,
          cache_creation_input_tokens: 0,
          cache_read_input_tokens: 0,
        },
        content: [
          {
            type: 'text',
            text: '<function=Bash><parameter=command>pwd</parameter></function>',
          },
        ],
      },
    } as const

    const converted = convertAssistantTextToolCallFallback(message)
    const expectedToolName = getPlatform() === 'windows' ? 'PowerShell' : 'Bash'

    expect(converted.message.content).toHaveLength(1)
    expect(converted.message.content[0]?.type).toBe('tool_use')
    expect((converted.message.content[0] as { name: string }).name).toBe(
      expectedToolName,
    )
    expect(
      ((converted.message.content[0] as { input: { command: string } }).input.command),
    ).toBe('pwd')
  })

  test('remaps fallback Bash tool calls to PowerShell on Windows', () => {
    const normalized = normalizeParsedToolCall(
      {
        name: 'Bash',
        input: { command: 'Get-Location' },
      },
      'windows',
    )

    expect(normalized.name).toBe('PowerShell')
    expect(normalized.input.command).toBe('Get-Location')
    expect(normalized.input.shell).toBe('powershell')
    expect(normalized.input.original_tool_name).toBe('Bash')
  })

  test('leaves non-tool assistant text unchanged', () => {
    const message = {
      type: 'assistant',
      uuid: 'u3',
      timestamp: '2026-04-06T00:00:00Z',
      message: {
        id: 'm3',
        type: 'message',
        role: 'assistant',
        model: 'test-model',
        stop_reason: 'end_turn',
        stop_sequence: null,
        usage: {
          input_tokens: 0,
          output_tokens: 0,
          cache_creation_input_tokens: 0,
          cache_read_input_tokens: 0,
        },
        content: [{ type: 'text', text: 'plain assistant text' }],
      },
    } as const

    expect(convertAssistantTextToolCallFallback(message)).toBe(message)
  })
})
