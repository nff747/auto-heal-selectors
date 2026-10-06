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

os.makedirs(os.path.join(SCRATCH, "src/engine"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "src/patcher"), exist_ok=True)

# -------------------------------------------------------------
# Commit 21: feat(engine): implement confidence evaluation
# -------------------------------------------------------------
conf_code = """import { HealCandidate } from '../types';

export class ConfidenceEvaluator {
  public static evaluateCandidate(
    candidate: HealCandidate,
    matchingElementCount: number
  ): number {
    let score = candidate.confidence;

    // Strict uniqueness check
    if (matchingElementCount === 1) {
      score = Math.min(1.0, score + 0.05); // Boost unique element
    } else if (matchingElementCount > 1) {
      // Ambiguity penalty: drop score proportionally
      const penalty = Math.min(0.4, 0.1 * (matchingElementCount - 1));
      score = Math.max(0.1, score - penalty);
    } else {
      // Zero elements found
      score = 0.0;
    }

    return Math.round(score * 100) / 100;
  }
}
"""
with open(os.path.join(SCRATCH, "src/engine/confidence.ts"), "w") as f:
    f.write(conf_code)

run_tests()
commit("feat(engine): implement confidence evaluation with uniqueness and ambiguity penalties")

# -------------------------------------------------------------
# Commit 22: feat(engine): implement multi-tier healing pipeline coordinator
# -------------------------------------------------------------
pipeline_code = """import { BaseHealStrategy } from '../strategies/base';
import { DynamicIdHealerStrategy } from '../strategies/id_healer';
import { SemanticTextHealerStrategy } from '../strategies/text_healer';
import { AriaRoleHealerStrategy } from '../strategies/aria_healer';
import { HierarchyAnchorHealerStrategy } from '../strategies/hierarchy_healer';
import { SpatialProximityHealerStrategy } from '../strategies/proximity_healer';
import { tokenizeSelector } from '../tokenizer';
import { ConfidenceEvaluator } from './confidence';
import { HealCandidate, HealerOptions, SelectorTokens } from '../types';

export class HealingPipeline {
  private strategies: BaseHealStrategy[];
  private options: HealerOptions;

  constructor(options: HealerOptions = {}) {
    this.options = {
      confidenceThreshold: 0.65,
      ...options
    };
    this.strategies = [
      new DynamicIdHealerStrategy(),
      new SemanticTextHealerStrategy(),
      new AriaRoleHealerStrategy(),
      new HierarchyAnchorHealerStrategy(),
      new SpatialProximityHealerStrategy()
    ];
  }

  public registerStrategy(strategy: BaseHealStrategy): void {
    this.strategies.push(strategy);
  }

  public async evaluate(
    brokenSelector: string,
    locatorResolver: (selector: string) => Promise<{ count: number; element?: any }>
  ): Promise<HealCandidate | null> {
    const tokens: SelectorTokens = tokenizeSelector(brokenSelector);
    const allCandidates: HealCandidate[] = [];

    for (const strat of this.strategies) {
      const candidates = await strat.generateCandidates({ tokens });
      for (const cand of candidates) {
        try {
          const res = await locatorResolver(cand.selector);
          if (res.count > 0) {
            const finalConfidence = ConfidenceEvaluator.evaluateCandidate(cand, res.count);
            if (finalConfidence >= (this.options.confidenceThreshold || 0.65)) {
              allCandidates.push({
                ...cand,
                confidence: finalConfidence
              });
            }
          }
        } catch {
          continue;
        }
      }

      // Early exit if a high-confidence match is discovered
      if (allCandidates.some(c => c.confidence >= 0.9)) {
        break;
      }
    }

    if (allCandidates.length === 0) return null;

    // Return the candidate with the highest confidence
    allCandidates.sort((a, b) => b.confidence - a.confidence);
    return allCandidates[0];
  }
}
"""
with open(os.path.join(SCRATCH, "src/engine/pipeline.ts"), "w") as f:
    f.write(pipeline_code)

run_tests()
commit("feat(engine): implement multi-tier healing pipeline coordinator")

# -------------------------------------------------------------
# Commit 23: test(engine): add test coverage for pipeline execution
# -------------------------------------------------------------
pipeline_test = """import { describe, it, expect } from 'vitest';
import { HealingPipeline } from '../src/engine/pipeline';
import { ConfidenceEvaluator } from '../src/engine/confidence';

describe('HealingPipeline & ConfidenceEvaluator', () => {
  it('ConfidenceEvaluator penalizes ambiguous multi-match elements', () => {
    const base = { selector: '.btn', strategy: 'test', confidence: 0.8, reason: 'test' };
    const unique = ConfidenceEvaluator.evaluateCandidate(base, 1);
    expect(unique).toBe(0.85); // 0.8 + 0.05 bonus

    const ambiguous = ConfidenceEvaluator.evaluateCandidate(base, 4);
    expect(ambiguous).toBeLessThan(0.8);
  });

  it('Pipeline resolves highest confidence candidate and halts early on strong match', async () => {
    const pipeline = new HealingPipeline({ confidenceThreshold: 0.7 });

    const mockResolver = async (sel: string) => {
      if (sel.includes('checkout_btn')) {
        return { count: 1 };
      }
      return { count: 0 };
    };

    const healed = await pipeline.evaluate('#checkout_btn_88219', mockResolver);
    expect(healed).not.toBeNull();
    expect(healed?.selector).toContain('checkout_btn');
    expect(healed?.confidence).toBeGreaterThanOrEqual(0.7);
  });

  it('Pipeline returns null if all candidates fail count check or threshold', async () => {
    const pipeline = new HealingPipeline({ confidenceThreshold: 0.99 });
    const mockResolver = async () => ({ count: 0 });

    const healed = await pipeline.evaluate('.non-existent', mockResolver);
    expect(healed).toBeNull();
  });
});
"""
with open(os.path.join(SCRATCH, "tests/pipeline.test.ts"), "w") as f:
    f.write(pipeline_test)

run_tests()
commit("test(engine): add test coverage for pipeline execution, confidence thresholds, and fallbacks")

# -------------------------------------------------------------
# Commit 24: feat(patcher): implement unified diff generator
# -------------------------------------------------------------
diff_code = """export interface DiffHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  lines: string[];
}

export function generateUnifiedDiff(params: {
  filePath: string;
  originalSelector: string;
  healedSelector: string;
  lineNumber: number;
  contextLines?: string[];
}): string {
  const lineNo = Math.max(1, params.lineNumber);
  const header = `--- a/${params.filePath}\\n+++ b/${params.filePath}`;
  const hunkHeader = `@@ -${lineNo},1 +${lineNo},1 @@`;
  const diffOld = `-  await page.locator('${params.originalSelector}').click();`;
  const diffNew = `+  await page.locator('${params.healedSelector}').click();`;

  return `${header}\\n${hunkHeader}\\n${diffOld}\\n${diffNew}`;
}
"""
with open(os.path.join(SCRATCH, "src/patcher/diff.ts"), "w") as f:
    f.write(diff_code)

run_tests()
commit("feat(patcher): implement unified diff generator with git-style hunk formatting")

# -------------------------------------------------------------
# Commit 25: test(patcher): add tests for unified diff generation
# -------------------------------------------------------------
diff_test = """import { describe, it, expect } from 'vitest';
import { generateUnifiedDiff } from '../src/patcher/diff';

describe('UnifiedDiffGenerator', () => {
  it('generates standard git-compatible unified diff hunks', () => {
    const diff = generateUnifiedDiff({
      filePath: 'tests/auth.spec.ts',
      originalSelector: '#submit_old_4812',
      healedSelector: '[data-testid="submit_old"]',
      lineNumber: 42
    });

    expect(diff).toContain('--- a/tests/auth.spec.ts');
    expect(diff).toContain('+++ b/tests/auth.spec.ts');
    expect(diff).toContain('@@ -42,1 +42,1 @@');
    expect(diff).toContain("-  await page.locator('#submit_old_4812').click();");
    expect(diff).toContain("+  await page.locator('[data-testid=\"submit_old\"]').click();");
  });
});
"""
with open(os.path.join(SCRATCH, "tests/diff.test.ts"), "w") as f:
    f.write(diff_test)

run_tests()
commit("test(patcher): add tests for unified diff generation and hunk calculations")

print("Block 5 (Commits 21-25) completed successfully.")
