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

# -------------------------------------------------------------
# Commit 16: feat(strategies): implement semantic text content healer
# -------------------------------------------------------------
text_healer_code = """import { BaseHealStrategy, StrategyContext } from './base';
import { HealCandidate } from '../types';

export class SemanticTextHealerStrategy extends BaseHealStrategy {
  public readonly name = 'semantic_text_content';
  public readonly baseWeight = 0.85;

  public generateCandidates(context: StrategyContext): HealCandidate[] {
    const candidates: HealCandidate[] = [];
    const text = context.tokens.text;
    if (!text) return candidates;

    const cleanText = text.trim();
    const tag = context.tokens.tagName || '';

    // 1. Exact Playwright text= match
    candidates.push({
      selector: tag ? `${tag}:has-text("${cleanText}")` : `text="${cleanText}"`,
      strategy: this.name,
      confidence: 0.88,
      reason: `Exact text match for '${cleanText}'`
    });

    // 2. Button or interactive element with aria-label
    if (tag === 'button' || tag === 'a' || !tag) {
      candidates.push({
        selector: `[aria-label*="${cleanText}" i]`,
        strategy: this.name,
        confidence: 0.82,
        reason: `Case-insensitive aria-label match for '${cleanText}'`
      });
    }

    return candidates;
  }
}
"""
with open(os.path.join(SCRATCH, "src/strategies/text_healer.ts"), "w") as f:
    f.write(text_healer_code)

run_tests()
commit("feat(strategies): implement semantic text content and button label healer")

# -------------------------------------------------------------
# Commit 17: feat(strategies): implement ARIA role and accessibility tree locator healer
# -------------------------------------------------------------
aria_healer_code = """import { BaseHealStrategy, StrategyContext } from './base';
import { HealCandidate } from '../types';

export class AriaRoleHealerStrategy extends BaseHealStrategy {
  public readonly name = 'aria_role_accessibility';
  public readonly baseWeight = 0.8;

  public generateCandidates(context: StrategyContext): HealCandidate[] {
    const candidates: HealCandidate[] = [];
    const role = context.tokens.role || context.tokens.attributes['role'];
    const text = context.tokens.text;

    if (role && text) {
      candidates.push({
        selector: `role=${role}[name="${text}"]`,
        strategy: this.name,
        confidence: 0.9,
        reason: `Explicit ARIA role '${role}' with name '${text}'`
      });
    } else if (role) {
      candidates.push({
        selector: `[role="${role}"]`,
        strategy: this.name,
        confidence: 0.6,
        reason: `Generic ARIA role '${role}'`
      });
    } else if (context.tokens.tagName === 'button') {
      candidates.push({
        selector: context.tokens.text ? `role=button[name="${context.tokens.text}"]` : 'role=button',
        strategy: this.name,
        confidence: 0.75,
        reason: 'Implicit button ARIA role mapping'
      });
    }

    return candidates;
  }
}
"""
with open(os.path.join(SCRATCH, "src/strategies/aria_healer.ts"), "w") as f:
    f.write(aria_healer_code)

run_tests()
commit("feat(strategies): implement ARIA role and accessibility tree locator healer")

# -------------------------------------------------------------
# Commit 18: feat(strategies): implement hierarchical anchor ancestor healer
# -------------------------------------------------------------
hier_healer_code = """import { BaseHealStrategy, StrategyContext } from './base';
import { HealCandidate } from '../types';

export class HierarchyAnchorHealerStrategy extends BaseHealStrategy {
  public readonly name = 'hierarchy_anchor_ancestor';
  public readonly baseWeight = 0.75;

  public generateCandidates(context: StrategyContext): HealCandidate[] {
    const candidates: HealCandidate[] = [];
    const targetTag = context.tokens.tagName || '*';

    // If classes exist, anchor with the first strong class
    if (context.tokens.classes.length > 0) {
      const primaryClass = context.tokens.classes[0];
      candidates.push({
        selector: `${targetTag}.${primaryClass}`,
        strategy: this.name,
        confidence: 0.7,
        reason: `Hierarchical tag and primary class '${primaryClass}'`
      });
    }

    // Anchor within common high-level semantic containers
    const containers = ['form', 'modal', 'dialog', 'header', 'footer', 'nav'];
    for (const c of containers) {
      if (context.tokens.text) {
        candidates.push({
          selector: `${c} >> ${targetTag}:has-text("${context.tokens.text}")`,
          strategy: this.name,
          confidence: 0.68,
          reason: `Scoped search within semantic container '${c}'`
        });
        break;
      }
    }

    return candidates;
  }
}
"""
with open(os.path.join(SCRATCH, "src/strategies/hierarchy_healer.ts"), "w") as f:
    f.write(hier_healer_code)

run_tests()
commit("feat(strategies): implement hierarchical anchor ancestor healer")

# -------------------------------------------------------------
# Commit 19: feat(strategies): implement 2D spatial proximity healer
# -------------------------------------------------------------
prox_healer_code = """import { BaseHealStrategy, StrategyContext } from './base';
import { HealCandidate } from '../types';

export class SpatialProximityHealerStrategy extends BaseHealStrategy {
  public readonly name = 'spatial_proximity_neighbor';
  public readonly baseWeight = 0.65;

  public generateCandidates(context: StrategyContext): HealCandidate[] {
    const candidates: HealCandidate[] = [];
    const text = context.tokens.text;

    if (text) {
      // Find interactive element near label text
      candidates.push({
        selector: `text="${text}" >> xpath=..//input | text="${text}" >> xpath=..//button`,
        strategy: this.name,
        confidence: 0.65,
        reason: `Interactive sibling/child relative to label '${text}'`
      });
    }

    return candidates;
  }
}
"""
with open(os.path.join(SCRATCH, "src/strategies/proximity_healer.ts"), "w") as f:
    f.write(prox_healer_code)

run_tests()
commit("feat(strategies): implement 2D spatial proximity and nearest-neighbor healer")

# -------------------------------------------------------------
# Commit 20: test(strategies): add unit tests for all 5 concrete healing strategies
# -------------------------------------------------------------
strat_test = """import { describe, it, expect } from 'vitest';
import { DynamicIdHealerStrategy } from '../src/strategies/id_healer';
import { SemanticTextHealerStrategy } from '../src/strategies/text_healer';
import { AriaRoleHealerStrategy } from '../src/strategies/aria_healer';
import { HierarchyAnchorHealerStrategy } from '../src/strategies/hierarchy_healer';
import { SpatialProximityHealerStrategy } from '../src/strategies/proximity_healer';
import { tokenizeSelector } from '../src/tokenizer';

describe('concrete healing strategy engines', () => {
  it('DynamicIdHealer cleans volatile dynamic ID suffixes', () => {
    const tokens = tokenizeSelector('#submit_btn_a9f812');
    const strat = new DynamicIdHealerStrategy();
    const candidates = strat.generateCandidates({ tokens });

    expect(candidates.length).toBeGreaterThan(0);
    expect(candidates[0].selector).toContain('submit_btn');
    expect(candidates[0].confidence).toBeGreaterThanOrEqual(0.85);
  });

  it('SemanticTextHealer creates Playwright text and aria-label fallbacks', () => {
    const tokens = tokenizeSelector('button:has-text("Submit Payment")');
    const strat = new SemanticTextHealerStrategy();
    const candidates = strat.generateCandidates({ tokens });

    expect(candidates.some(c => c.selector.includes('Submit Payment'))).toBe(true);
    expect(candidates.some(c => c.selector.includes('aria-label'))).toBe(true);
  });

  it('AriaRoleHealer maps explicit and implicit accessible roles', () => {
    const tokens = tokenizeSelector('role=button[name="Save"]');
    const strat = new AriaRoleHealerStrategy();
    const candidates = strat.generateCandidates({ tokens });

    expect(candidates[0].selector).toBe('role=button[name="Save"]');
    expect(candidates[0].confidence).toBe(0.9);
  });

  it('HierarchyAnchorHealer generates scoped container locators', () => {
    const tokens = tokenizeSelector('button.checkout-btn:has-text("Buy")');
    const strat = new HierarchyAnchorHealerStrategy();
    const candidates = strat.generateCandidates({ tokens });

    expect(candidates.some(c => c.selector.includes('checkout-btn'))).toBe(true);
  });

  it('SpatialProximityHealer resolves adjacent form controls', () => {
    const tokens = tokenizeSelector('label:has-text("Username")');
    const strat = new SpatialProximityHealerStrategy();
    const candidates = strat.generateCandidates({ tokens });

    expect(candidates.length).toBe(1);
    expect(candidates[0].selector).toContain('xpath=..//input');
  });
});
"""
with open(os.path.join(SCRATCH, "tests/strategies.test.ts"), "w") as f:
    f.write(strat_test)

run_tests()
commit("test(strategies): add unit tests for all 5 concrete healing strategy engines")

print("Block 4 (Commits 16-20) completed successfully.")
