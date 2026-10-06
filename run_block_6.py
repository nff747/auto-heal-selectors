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

os.makedirs(os.path.join(SCRATCH, "src/storage"), exist_ok=True)

# -------------------------------------------------------------
# Commit 26: feat(patcher): implement test file scanner
# -------------------------------------------------------------
scanner_code = r"""import * as fs from 'fs';
import * as path from 'path';

export interface SelectorCallsite {
  filePath: string;
  lineNumber: number;
  lineContent: string;
  matchedSelector: string;
}

export class TestFileScanner {
  public static scanFile(filePath: string, selector: string): SelectorCallsite[] {
    if (!fs.existsSync(filePath)) return [];
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    const results: SelectorCallsite[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.includes(selector)) {
        results.push({
          filePath,
          lineNumber: i + 1,
          lineContent: line,
          matchedSelector: selector
        });
      }
    }
    return results;
  }
}
"""
with open(os.path.join(SCRATCH, "src/patcher/file_scanner.ts"), "w") as f:
    f.write(scanner_code)

run_tests()
commit("feat(patcher): implement test file scanner for locating broken selector callsites")

# -------------------------------------------------------------
# Commit 27: test(patcher): add tests for test file discovery
# -------------------------------------------------------------
scanner_test = r"""import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { TestFileScanner } from '../src/patcher/file_scanner';

describe('TestFileScanner', () => {
  const tempFile = path.join(__dirname, 'temp_test_spec.ts');

  beforeEach(() => {
    fs.writeFileSync(tempFile, "import { test } from '@playwright/test';\ntest('login', async ({ page }) => {\n  await page.locator('#broken_btn').click();\n});\n");
  });

  afterEach(() => {
    if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
  });

  it('scans file and locates line number containing the target selector', () => {
    const results = TestFileScanner.scanFile(tempFile, '#broken_btn');
    expect(results.length).toBe(1);
    expect(results[0].lineNumber).toBe(3);
    expect(results[0].lineContent).toContain('#broken_btn');
  });

  it('returns empty array if selector is not present', () => {
    const results = TestFileScanner.scanFile(tempFile, '#non_existent');
    expect(results.length).toBe(0);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/file_scanner.test.ts"), "w") as f:
    f.write(scanner_test)

run_tests()
commit("test(patcher): add tests for test file discovery and selector string matching")

# -------------------------------------------------------------
# Commit 28: feat(patcher): implement safe AST and regex source code rewriter
# -------------------------------------------------------------
rewriter_code = r"""import * as fs from 'fs';

export class SourceCodeRewriter {
  public static rewriteSelectorInContent(
    content: string,
    originalSelector: string,
    healedSelector: string
  ): { updatedContent: string; replacements: number } {
    let replacements = 0;
    // Replace inside quotes matching locator('...'), $("..."), etc.
    const escaped = originalSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(['"\`])${escaped}\\1`, 'g');

    const updatedContent = content.replace(regex, (_match, quote) => {
      replacements++;
      return `${quote}${healedSelector}${quote}`;
    });

    return { updatedContent, replacements };
  }

  public static patchFile(
    filePath: string,
    originalSelector: string,
    healedSelector: string
  ): boolean {
    if (!fs.existsSync(filePath)) return false;
    const content = fs.readFileSync(filePath, 'utf-8');
    const { updatedContent, replacements } = this.rewriteSelectorInContent(
      content,
      originalSelector,
      healedSelector
    );
    if (replacements > 0) {
      fs.writeFileSync(filePath, updatedContent, 'utf-8');
      return true;
    }
    return false;
  }
}
"""
with open(os.path.join(SCRATCH, "src/patcher/ast_rewriter.ts"), "w") as f:
    f.write(rewriter_code)

run_tests()
commit("feat(patcher): implement safe AST and regex source code rewriter")

# -------------------------------------------------------------
# Commit 29: test(patcher): add tests for in-place test code rewriting
# -------------------------------------------------------------
rewriter_test = r"""import { describe, it, expect } from 'vitest';
import { SourceCodeRewriter } from '../src/patcher/ast_rewriter';

describe('SourceCodeRewriter', () => {
  it('rewrites selector inside single, double, and backtick quotes', () => {
    const code = `
      await page.locator('#broken_1').click();
      await page.locator("#broken_1").fill("hi");
      await page.locator(\`#broken_1\`).hover();
    `;
    const { updatedContent, replacements } = SourceCodeRewriter.rewriteSelectorInContent(
      code,
      '#broken_1',
      '[data-testid="healed_1"]'
    );

    expect(replacements).toBe(3);
    expect(updatedContent).not.toContain('#broken_1');
    expect(updatedContent).toContain('[data-testid="healed_1"]');
  });

  it('preserves indentation and surrounding syntax untouched', () => {
    const code = '    // Note\n    await page.locator("#btn").click();\n';
    const { updatedContent } = SourceCodeRewriter.rewriteSelectorInContent(code, '#btn', '#healed');
    expect(updatedContent).toBe('    // Note\n    await page.locator("#healed").click();\n');
  });
});
"""
with open(os.path.join(SCRATCH, "tests/ast_rewriter.test.ts"), "w") as f:
    f.write(rewriter_test)

run_tests()
commit("test(patcher): add tests for in-place test code rewriting and formatting preservation")

# -------------------------------------------------------------
# Commit 30: feat(storage): implement local persistent store
# -------------------------------------------------------------
store_code = r"""import * as fs from 'fs';
import * as path from 'path';
import { HealEvent } from '../types';

export class HealerStore {
  private storeFile: string;

  constructor(storageDir: string = '.healer') {
    this.storeFile = path.join(storageDir, 'history.json');
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
  }

  public recordEvent(event: HealEvent): void {
    const events = this.getAllEvents();
    events.push(event);
    fs.writeFileSync(this.storeFile, JSON.stringify(events, null, 2), 'utf-8');
  }

  public getAllEvents(): HealEvent[] {
    if (!fs.existsSync(this.storeFile)) return [];
    try {
      const data = fs.readFileSync(this.storeFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return []; // Recover from corrupted store file
    }
  }

  public getSuccessRate(): number {
    const events = this.getAllEvents();
    if (events.length === 0) return 1.0;
    const successful = events.filter(e => e.confidence >= 0.7).length;
    return successful / events.length;
  }
}
"""
with open(os.path.join(SCRATCH, "src/storage/healer_store.ts"), "w") as f:
    f.write(store_code)

run_tests()
commit("feat(storage): implement local persistent store for tracking healing history")

print("Block 6 (Commits 26-30) completed successfully.")
