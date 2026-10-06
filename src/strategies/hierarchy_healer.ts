import { BaseHealStrategy, StrategyContext } from './base';
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
