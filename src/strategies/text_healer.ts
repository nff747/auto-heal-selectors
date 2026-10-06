import { BaseHealStrategy, StrategyContext } from './base';
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
