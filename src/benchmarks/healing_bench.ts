import { levenshteinDistance, normalizedSimilarity } from '../levenshtein';
import { tokenizeSelector } from '../tokenizer';
import { DynamicIdHealerStrategy } from '../strategies/id_healer';

export function runMicroBenchmark(): { opsPerSec: number; avgLatencyMs: number } {
  const iterations = 5000;
  const start = performance.now();

  const idStrat = new DynamicIdHealerStrategy();
  for (let i = 0; i < iterations; i++) {
    const tokens = tokenizeSelector(`button#checkout_btn_${i}_a99f.primary[data-action="buy"]`);
    idStrat.generateCandidates({ tokens });
    levenshteinDistance('checkout_btn_123', 'checkout_btn_124');
    normalizedSimilarity('checkout_btn_123', 'checkout_btn_124');
  }

  const durationMs = performance.now() - start;
  const avgLatencyMs = durationMs / iterations;
  const opsPerSec = Math.round((iterations / (durationMs / 1000)));

  return { opsPerSec, avgLatencyMs };
}
