import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { CLICommands } from '../src/cli/commands';
import { HealerStore } from '../src/storage/healer_store';

describe('CLICommands', () => {
  const testDir = path.join(__dirname, '.test_cli_store');

  beforeEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  it('generates reports across different formats', () => {
    const store = new HealerStore(testDir);
    store.recordEvent({
      originalSelector: '#foo',
      healedSelector: '#bar',
      strategy: 'id',
      confidence: 0.95,
      action: 'click',
      timestamp: Date.now()
    });

    const md = CLICommands.report('markdown', testDir);
    expect(md).toContain('#foo');
    expect(md).toContain('#bar');

    const json = CLICommands.report('json', testDir);
    expect(JSON.parse(json).totalHealed).toBe(1);

    const html = CLICommands.report('html', testDir);
    expect(html).toContain('<!DOCTYPE html>');
  });

  it('cleans storage directory cleanly', () => {
    new HealerStore(testDir);
    expect(fs.existsSync(testDir)).toBe(true);

    const cleaned = CLICommands.clean(testDir);
    expect(cleaned).toBe(true);
    expect(fs.existsSync(testDir)).toBe(false);
  });
});
