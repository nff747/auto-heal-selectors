import { BaseHealStrategy, StrategyContext } from './base';
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
