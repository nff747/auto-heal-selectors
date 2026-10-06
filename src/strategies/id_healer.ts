import { BaseHealStrategy, StrategyContext } from './base';
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
