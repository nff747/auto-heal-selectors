import { describe, it, expect } from 'vitest';
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
