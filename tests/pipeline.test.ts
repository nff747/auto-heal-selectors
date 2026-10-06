import { describe, it, expect } from 'vitest';
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
