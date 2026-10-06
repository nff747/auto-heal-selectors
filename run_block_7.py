import os
import subprocess
import sys

SCRATCH = "/home/n1khy/.gemini/antigravity/scratch/auto-heal-selectors"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    return res.stdout.strip()

def run_tests():
    res = subprocess.run("npm test", shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print("TESTS FAILED:")
        print(res.stdout)
        print(res.stderr)
        sys.exit(1)
    return True

def commit(msg):
    run_cmd("git add -A")
    out = run_cmd(f'git commit -m "{msg}"')
    print(f"Committed: {msg}")

os.makedirs(os.path.join(SCRATCH, "src/reporters"), exist_ok=True)

# -------------------------------------------------------------
# Commit 31: test(storage): add unit tests for healing telemetry persistence
# -------------------------------------------------------------
storage_test = r"""import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { HealerStore } from '../src/storage/healer_store';

describe('HealerStore', () => {
  const testDir = path.join(__dirname, '.test_healer_store');

  beforeEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  it('records events and computes healing success rate', () => {
    const store = new HealerStore(testDir);
    expect(store.getAllEvents().length).toBe(0);
    expect(store.getSuccessRate()).toBe(1.0);

    store.recordEvent({
      originalSelector: '#a',
      healedSelector: '#b',
      strategy: 'id',
      confidence: 0.9,
      action: 'click',
      timestamp: Date.now()
    });

    store.recordEvent({
      originalSelector: '#x',
      healedSelector: '#y',
      strategy: 'text',
      confidence: 0.4,
      action: 'fill',
      timestamp: Date.now()
    });

    expect(store.getAllEvents().length).toBe(2);
    expect(store.getSuccessRate()).toBe(0.5);
  });

  it('recovers gracefully from corrupted store file', () => {
    const store = new HealerStore(testDir);
    fs.writeFileSync(path.join(testDir, 'history.json'), '{ invalid json ...', 'utf-8');
    expect(store.getAllEvents()).toEqual([]);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/storage.test.ts"), "w") as f:
    f.write(storage_test)

run_tests()
commit("test(storage): add unit tests for healing telemetry persistence and corruption recovery")

# -------------------------------------------------------------
# Commit 32: feat(reporters): implement machine-readable JSON summary exporter
# -------------------------------------------------------------
json_rep_code = r"""import { HealEvent } from '../types';

export interface JSONReportSummary {
  totalHealed: number;
  averageConfidence: number;
  strategyBreakdown: Record<string, number>;
  events: HealEvent[];
}

export function generateJSONReport(events: HealEvent[]): string {
  const breakdown: Record<string, number> = {};
  let totalConf = 0;

  for (const e of events) {
    breakdown[e.strategy] = (breakdown[e.strategy] || 0) + 1;
    totalConf += e.confidence;
  }

  const summary: JSONReportSummary = {
    totalHealed: events.length,
    averageConfidence: events.length > 0 ? Math.round((totalConf / events.length) * 100) / 100 : 1.0,
    strategyBreakdown: breakdown,
    events
  };

  return JSON.stringify(summary, null, 2);
}
"""
with open(os.path.join(SCRATCH, "src/reporters/json_reporter.ts"), "w") as f:
    f.write(json_rep_code)

run_tests()
commit("feat(reporters): implement machine-readable JSON summary exporter for CI/CD")

# -------------------------------------------------------------
# Commit 33: feat(reporters): implement GitHub PR markdown reporter
# -------------------------------------------------------------
md_rep_code = r"""import { HealEvent } from '../types';

export function generateMarkdownReport(events: HealEvent[]): string {
  if (events.length === 0) {
    return '### 🛡️ Auto-Heal Selectors: 0 Selectors Required Remediation\n\nAll locators matched cleanly during test execution.';
  }

  let md = `### 🤖 Auto-Heal Selectors: Remediation Summary\n\n`;
  md += `| Original Selector | Healed Selector | Strategy | Confidence | Action |\n`;
  md += `| :--- | :--- | :--- | :---: | :---: |\n`;

  for (const e of events) {
    const badge = e.confidence >= 0.8 ? '🟢' : e.confidence >= 0.6 ? '🟡' : '🔴';
    md += `| \`${e.originalSelector}\` | \`${e.healedSelector}\` | ${e.strategy} | ${badge} ${(e.confidence * 100).toFixed(0)}% | \`${e.action}\` |\n`;
  }

  md += `\n*Run \`npx auto-heal patch\` to apply healed locators directly to your test files.*\n`;
  return md;
}
"""
with open(os.path.join(SCRATCH, "src/reporters/markdown_reporter.ts"), "w") as f:
    f.write(md_rep_code)

run_tests()
commit("feat(reporters): implement GitHub PR / Job Summary markdown reporter")

# -------------------------------------------------------------
# Commit 34: feat(reporters): implement standalone interactive HTML report dashboard
# -------------------------------------------------------------
html_rep_code = r"""import { HealEvent } from '../types';

export function generateHTMLReport(events: HealEvent[]): string {
  const rows = events.map(e => `
    <tr>
      <td class="code">${escapeHtml(e.originalSelector)}</td>
      <td class="code healed">${escapeHtml(e.healedSelector)}</td>
      <td><span class="badge strategy">${escapeHtml(e.strategy)}</span></td>
      <td><span class="badge ${e.confidence >= 0.8 ? 'high' : 'med'}">${(e.confidence * 100).toFixed(0)}%</span></td>
      <td><code>${escapeHtml(e.action)}</code></td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Auto-Heal Selectors Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }
    h1 { color: #58a6ff; font-size: 1.5rem; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: #161b22; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #30363d; }
    th { background: #21262d; color: #8b949e; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
    .code { font-family: monospace; font-size: 0.9rem; }
    .healed { color: #3fb950; font-weight: bold; }
    .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge.high { background: #238636; color: white; }
    .badge.med { background: #d29922; color: black; }
    .badge.strategy { background: #388bfd33; color: #58a6ff; }
  </style>
</head>
<body>
  <h1>🛡️ Auto-Heal Selectors Telemetry Report</h1>
  <p>Total Elements Remediated: <strong>${events.length}</strong></p>
  <table>
    <thead>
      <tr>
        <th>Broken Selector</th>
        <th>Healed Replacement</th>
        <th>Strategy</th>
        <th>Confidence</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      ${rows}
    </tbody>
  </table>
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
"""
with open(os.path.join(SCRATCH, "src/reporters/html_reporter.ts"), "w") as f:
    f.write(html_rep_code)

run_tests()
commit("feat(reporters): implement standalone interactive HTML report dashboard")

# -------------------------------------------------------------
# Commit 35: test(reporters): add tests for JSON, Markdown, and HTML report generators
# -------------------------------------------------------------
rep_test = r"""import { describe, it, expect } from 'vitest';
import { generateJSONReport } from '../src/reporters/json_reporter';
import { generateMarkdownReport } from '../src/reporters/markdown_reporter';
import { generateHTMLReport } from '../src/reporters/html_reporter';
import { HealEvent } from '../src/types';

describe('telemetry reporters', () => {
  const events: HealEvent[] = [
    {
      originalSelector: '#submit_old',
      healedSelector: '[data-testid="submit_new"]',
      strategy: 'dynamic_id_attribute',
      confidence: 0.9,
      action: 'click',
      timestamp: Date.now()
    }
  ];

  it('generates structured JSON summary with metrics', () => {
    const jsonStr = generateJSONReport(events);
    const parsed = JSON.parse(jsonStr);
    expect(parsed.totalHealed).toBe(1);
    expect(parsed.averageConfidence).toBe(0.9);
    expect(parsed.strategyBreakdown['dynamic_id_attribute']).toBe(1);
  });

  it('generates Markdown summary table', () => {
    const md = generateMarkdownReport(events);
    expect(md).toContain('| `#submit_old` | `[data-testid="submit_new"]` |');
    expect(md).toContain('90%');
  });

  it('generates HTML report document with escaped content', () => {
    const html = generateHTMLReport(events);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('#submit_old');
    expect(html).toContain('[data-testid=&quot;submit_new&quot;]');
  });
});
"""
with open(os.path.join(SCRATCH, "tests/reporters.test.ts"), "w") as f:
    f.write(rep_test)

run_tests()
commit("test(reporters): add tests for JSON, Markdown, and HTML report generators")

print("Block 7 (Commits 31-35) completed successfully.")
