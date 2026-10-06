import { BaseHealStrategy } from '../strategies/base';
import { DynamicIdHealerStrategy } from '../strategies/id_healer';
import { SemanticTextHealerStrategy } from '../strategies/text_healer';
import { AriaRoleHealerStrategy } from '../strategies/aria_healer';
import { HierarchyAnchorHealerStrategy } from '../strategies/hierarchy_healer';
import { SpatialProximityHealerStrategy } from '../strategies/proximity_healer';
import { tokenizeSelector } from '../tokenizer';
import { ConfidenceEvaluator } from './confidence';
import { HealCandidate, HealerOptions, SelectorTokens } from '../types';

export class HealingPipeline {
  private strategies: BaseHealStrategy[];
  private options: HealerOptions;

  constructor(options: HealerOptions = {}) {
    this.options = {
      confidenceThreshold: 0.65,
      ...options
    };
    this.strategies = [
      new DynamicIdHealerStrategy(),
      new SemanticTextHealerStrategy(),
      new AriaRoleHealerStrategy(),
      new HierarchyAnchorHealerStrategy(),
      new SpatialProximityHealerStrategy()
    ];
  }

  public registerStrategy(strategy: BaseHealStrategy): void {
    this.strategies.push(strategy);
  }

  public async evaluate(
    brokenSelector: string,
    locatorResolver: (selector: string) => Promise<{ count: number; element?: any }>
  ): Promise<HealCandidate | null> {
    const tokens: SelectorTokens = tokenizeSelector(brokenSelector);
    const allCandidates: HealCandidate[] = [];

    for (const strat of this.strategies) {
      const candidates = await strat.generateCandidates({ tokens });
      for (const cand of candidates) {
        try {
          const res = await locatorResolver(cand.selector);
          if (res.count > 0) {
            const finalConfidence = ConfidenceEvaluator.evaluateCandidate(cand, res.count);
            if (finalConfidence >= (this.options.confidenceThreshold || 0.65)) {
              allCandidates.push({
                ...cand,
                confidence: finalConfidence
              });
            }
          }
        } catch {
          continue;
        }
      }

      // Early exit if a high-confidence match is discovered
      if (allCandidates.some(c => c.confidence >= 0.9)) {
        break;
      }
    }

    if (allCandidates.length === 0) return null;

    // Return the candidate with the highest confidence
    allCandidates.sort((a, b) => b.confidence - a.confidence);
    return allCandidates[0];
  }
}
