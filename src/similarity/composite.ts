import { calculatePathSimilarity } from './structural';
import { calculateAttributeSimilarity } from './attribute';
import { calculateTextSimilarity } from './text';

export interface SimilarityWeights {
  structural: number;
  attribute: number;
  text: number;
}

export const DEFAULT_WEIGHTS: SimilarityWeights = {
  structural: 0.3,
  attribute: 0.4,
  text: 0.3
};

export function calculateCompositeSimilarity(params: {
  expectedPath?: string[];
  actualPath?: string[];
  expectedAttrs: Record<string, string>;
  actualAttrs: Record<string, string>;
  expectedClasses: string[];
  actualClasses: string[];
  expectedText?: string;
  actualText?: string;
  weights?: Partial<SimilarityWeights>;
}): number {
  const w: SimilarityWeights = { ...DEFAULT_WEIGHTS, ...params.weights };
  const normTotal = w.structural + w.attribute + w.text;
  const wS = w.structural / normTotal;
  const wA = w.attribute / normTotal;
  const wT = w.text / normTotal;

  const sScore = params.expectedPath && params.actualPath 
    ? calculatePathSimilarity(params.expectedPath, params.actualPath)
    : 0.5;

  const aScore = calculateAttributeSimilarity(
    params.expectedAttrs,
    params.actualAttrs,
    params.expectedClasses,
    params.actualClasses
  );

  const tScore = calculateTextSimilarity(
    params.expectedText || '',
    params.actualText || ''
  );

  return wS * sScore + wA * aScore + wT * tScore;
}
