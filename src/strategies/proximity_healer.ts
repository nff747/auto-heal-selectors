import { BaseHealStrategy, StrategyContext } from './base';
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
