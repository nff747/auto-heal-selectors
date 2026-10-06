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

os.makedirs(os.path.join(SCRATCH, "src/strategies"), exist_ok=True)

# -------------------------------------------------------------
# Commit 13: test(similarity): add comprehensive test suite
# -------------------------------------------------------------
sim_test = """import { describe, it, expect } from 'vitest';
import { calculatePathSimilarity } from '../src/similarity/structural';
import { calculateAttributeSimilarity } from '../src/similarity/attribute';
import { calculateTextSimilarity } from '../src/similarity/text';
import { calculateCompositeSimilarity } from '../src/similarity/composite';

describe('similarity metric engine', () => {
  it('computes path similarity for common DOM structures', () => {
    const pathA = ['html', 'body', 'div#app', 'button.submit'];
    const pathB = ['html', 'body', 'div#app', 'button.submit'];
    expect(calculatePathSimilarity(pathA, pathB)).toBe(1.0);

    const pathC = ['html', 'body', 'section.main', 'button.submit'];
    expect(calculatePathSimilarity(pathA, pathC)).toBeGreaterThan(0.35);
  });

  it('computes attribute and class Jaccard similarity', () => {
    const attrsA = { type: 'button', 'data-action': 'save' };
    const attrsB = { type: 'button', 'data-action': 'save' };
    const score = calculateAttributeSimilarity(attrsA, attrsB, ['btn', 'btn-primary'], ['btn', 'btn-primary']);
    expect(score).toBe(1.0);

    const scorePartial = calculateAttributeSimilarity(attrsA, { type: 'submit' }, ['btn'], ['btn', 'btn-danger']);
    expect(scorePartial).toBeLessThan(0.7);
  });

  it('computes fuzzy and substring text similarity', () => {
    expect(calculateTextSimilarity('Checkout', 'Checkout Now')).toBeGreaterThanOrEqual(0.85);
    expect(calculateTextSimilarity('Sign In', 'Sign Out')).toBeGreaterThan(0.5);
    expect(calculateTextSimilarity('Delete Account', 'Settings')).toBeLessThan(0.4);
  });

  it('evaluates weighted composite similarity', () => {
    const composite = calculateCompositeSimilarity({
      expectedPath: ['body', 'form', 'button'],
      actualPath: ['body', 'form', 'button'],
      expectedAttrs: { type: 'submit' },
      actualAttrs: { type: 'submit' },
      expectedClasses: ['btn'],
      actualClasses: ['btn'],
      expectedText: 'Submit',
      actualText: 'Submit'
    });
    expect(composite).toBe(1.0);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/similarity.test.ts"), "w") as f:
    f.write(sim_test)

run_tests()
commit("test(similarity): add comprehensive test suite for structural, attribute, and text similarity")

# -------------------------------------------------------------
# Commit 14: feat(strategies): define abstract base healing strategy contract
# -------------------------------------------------------------
strategy_base_code = """import { HealCandidate, SelectorTokens, SerializedDOMNode } from '../types';

export interface StrategyContext {
  tokens: SelectorTokens;
  snapshotNode?: SerializedDOMNode;
  availableNodes?: SerializedDOMNode[];
}

export abstract class BaseHealStrategy {
  public abstract readonly name: string;
  public abstract readonly baseWeight: number;

  public abstract generateCandidates(context: StrategyContext): Promise<HealCandidate[]> | HealCandidate[];
}
"""
with open(os.path.join(SCRATCH, "src/strategies/base.ts"), "w") as f:
    f.write(strategy_base_code)

run_tests()
commit("feat(strategies): define abstract base healing strategy contract")

# -------------------------------------------------------------
# Commit 15: feat(strategies): implement dynamic ID stripper
# -------------------------------------------------------------
id_healer_code = """import { BaseHealStrategy, StrategyContext } from './base';
import { HealCandidate } from '../types';

export class DynamicIdHealerStrategy extends BaseHealStrategy {
  public readonly name = 'dynamic_id_attribute';
  public readonly baseWeight = 0.9;

  public generateCandidates(context: StrategyContext): HealCandidate[] {
    const candidates: HealCandidate[] = [];
    const id = context.tokens.id || context.tokens.attributes['id'] || context.tokens.attributes['data-testid'];

    if (!id) return candidates;

    // Detect numeric or hash suffixes e.g. "submit_btn_38291" -> "submit_btn"
    const cleaned = id.replace(/[-_][0-9a-fA-F]{4,}$/, '').replace(/[-_][0-9]+$/, '');

    // 1. Partial attribute substring selector
    candidates.push({
      selector: `[data-testid*="${cleaned}"], [id*="${cleaned}"]`,
      strategy: this.name,
      confidence: cleaned === id ? 0.95 : 0.85,
      reason: `Stripped volatile dynamic suffix from identifier '${id}' to '${cleaned}'`
    });

    // 2. Prefix wildcard selector
    if (cleaned.length >= 3) {
      candidates.push({
        selector: `[id^="${cleaned}"], [data-testid^="${cleaned}"]`,
        strategy: this.name,
        confidence: 0.8,
        reason: `Matched stable prefix '${cleaned}'`
      });
    }

    return candidates;
  }
}
"""
with open(os.path.join(SCRATCH, "src/strategies/id_healer.ts"), "w") as f:
    f.write(id_healer_code)

run_tests()
commit("feat(strategies): implement dynamic ID stripper and stable attribute healer")

print("Commits 13-15 completed successfully.")
