import { HealCandidate } from '../types';

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
