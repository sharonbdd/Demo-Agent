import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'fs'
import { tmpdir } from 'os'
import { basename, join } from 'path'
import { resetStateForTests, setOriginalCwd } from '../bootstrap/state.js'
import { enableConfigs } from './config.js'
import {
  clearMemoryFileCaches,
  getClaudeMds,
  getMemoryFiles,
  isMemoryFilePath,
} from './claudemd.js'

const AI_WORKFLOW_FILES = [
  'AGENTS.md',
  'PLAN.md',
  'PROGRESS.md',
  'NEXT_TASKS.md',
] as const

describe('AI WORKFLOW project memory loading', () => {
  let workspaceDir: string

  beforeEach(() => {
    enableConfigs()
    resetStateForTests()
    clearMemoryFileCaches()
    workspaceDir = mkdtempSync(join(tmpdir(), 'openclaude-ai-workflow-'))
  })

  afterEach(() => {
    clearMemoryFileCaches()
    rmSync(workspaceDir, { recursive: true, force: true })
  })

  test('loads AI WORKFLOW files as ordered project instructions', async () => {
    const workflowDir = join(workspaceDir, 'AI WORKFLOW')
    mkdirSync(workflowDir, { recursive: true })
    writeFileSync(join(workflowDir, 'AGENTS.md'), '# Agents\nagent rules')
    writeFileSync(join(workflowDir, 'PLAN.md'), '# Plan\ncurrent plan')
    writeFileSync(join(workflowDir, 'PROGRESS.md'), '# Progress\ncurrent progress')
    writeFileSync(join(workflowDir, 'NEXT_TASKS.md'), '# Next\nqueued work')

    setOriginalCwd(workspaceDir)
    clearMemoryFileCaches()

    const files = await getMemoryFiles()
    const workflowFiles = files.filter(file =>
      file.path.startsWith(workspaceDir) &&
      file.path.includes(`${join('AI WORKFLOW', '')}`),
    )

    expect(workflowFiles.map(file => basename(file.path))).toEqual(
      AI_WORKFLOW_FILES,
    )
    expect(workflowFiles.every(file => file.type === 'Project')).toBe(true)

    const prompt = getClaudeMds(workflowFiles)
    expect(prompt).toContain('Contents of')
    expect(prompt.indexOf('AGENTS.md')).toBeLessThan(prompt.indexOf('PLAN.md'))
    expect(prompt.indexOf('PLAN.md')).toBeLessThan(prompt.indexOf('PROGRESS.md'))
    expect(prompt.indexOf('PROGRESS.md')).toBeLessThan(
      prompt.indexOf('NEXT_TASKS.md'),
    )
  })

  test('recognizes AI WORKFLOW files as memory files', () => {
    const workflowPath = join(workspaceDir, 'AI WORKFLOW', 'AGENTS.md')
    const unrelatedPath = join(workspaceDir, 'AI WORKFLOW', 'NOTES.md')

    expect(isMemoryFilePath(workflowPath)).toBe(true)
    expect(isMemoryFilePath(unrelatedPath)).toBe(false)
  })
})
