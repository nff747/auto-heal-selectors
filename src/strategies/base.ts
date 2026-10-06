import { HealCandidate, SelectorTokens, SerializedDOMNode } from '../types';

export interface StrategyContext {
  tokens: SelectorTokens;
  snapshotNode?: SerializedDOMNode;
  availableNodes?: SerializedDOMNode[];
}

export abstract class BaseHealStrategy {
  public abstract readonly name: string;
  public abstract readonly baseWeight: number;

  public abstract generateCandidates(context: StrategyContext): Promise<HealCandidate[]> | HealCandidate[];
}
