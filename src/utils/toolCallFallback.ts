import { randomUUID } from 'crypto'
import type { ToolUseBlock } from '@anthropic-ai/sdk/resources/index.mjs'
import type { AssistantMessage } from '../types/message.js'
import { BASH_TOOL_NAME } from '../tools/BashTool/toolName.js'
import { POWERSHELL_TOOL_NAME } from '../tools/PowerShellTool/toolName.js'
import { extractTextContent } from './messages.js'
import { getPlatform } from './platform.js'
import { normalizeShellToolName } from './shell/shellToolUtils.js'

type ParsedToolCall = {
  name: string
  input: Record<string, string>
}

function stripToolCallWrapper(text: string): string {
  return text
    .replace(/^<tool_call>\s*/i, '')
    .replace(/\s*<\/tool_call>$/i, '')
    .trim()
}

export function parseXmlStyleToolCall(text: string): ParsedToolCall | null {
  const normalized = stripToolCallWrapper(text.trim())
  const functionMatch = normalized.match(
    /^<function=([A-Za-z0-9_:-]+)>\s*([\s\S]*?)\s*<\/function>$/i,
  )
  if (!functionMatch) return null

  const [, name, body] = functionMatch
  const input: Record<string, string> = {}
  const parameterPattern =
    /<parameter=([A-Za-z0-9_:-]+)>\s*([\s\S]*?)\s*<\/parameter>/gi

  let sawParameter = false
  for (const match of body.matchAll(parameterPattern)) {
    sawParameter = true
    input[match[1]] = match[2].trim()
  }

  if (!sawParameter) return null
  return { name, input }
}

export function normalizeParsedToolCall(
  parsed: ParsedToolCall,
  currentPlatform: string = getPlatform(),
): ParsedToolCall {
  const normalizedName = normalizeShellToolName(
    parsed.name,
    currentPlatform,
    currentPlatform === 'windows',
  )
  if (normalizedName === parsed.name) {
    return parsed
  }

  return {
    name: normalizedName,
    input: {
      ...parsed.input,
      ...(normalizedName === POWERSHELL_TOOL_NAME && parsed.name === BASH_TOOL_NAME
        ? {
            shell: 'powershell',
            original_tool_name: parsed.name,
          }
        : {}),
    },
  }
}

export function convertAssistantTextToolCallFallback(
  message: AssistantMessage,
): AssistantMessage {
  const parsed = parseXmlStyleToolCall(extractTextContent(message.message.content))
  if (!parsed) return message
  const normalized = normalizeParsedToolCall(parsed)

  const toolUseBlock = {
    type: 'tool_use',
    id: `toolu_${randomUUID()}`,
    name: normalized.name,
    input: normalized.input,
  } as ToolUseBlock

  return {
    ...message,
    message: {
      ...message.message,
      content: [toolUseBlock],
    },
  }
}
