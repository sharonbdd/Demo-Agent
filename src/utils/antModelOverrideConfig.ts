import type { EffortValue } from './effort.js'

export type AntModelOverrideConfig = {
  defaultModel?: string
  defaultModelEffortLevel?: EffortValue
  defaultSystemPromptSuffix?: string
}

// Open builds import this module directly. Keep the stub checked in so fresh
// clones and packaged builds resolve the path even without Anthropic internals.
export function getAntModelOverrideConfig(): AntModelOverrideConfig | null {
  return null
}
