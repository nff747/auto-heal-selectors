import { normalizedSimilarity } from '../levenshtein';

export function calculateAttributeSimilarity(
  expectedAttrs: Record<string, string>,
  actualAttrs: Record<string, string>,
  expectedClasses: string[],
  actualClasses: string[]
): number {
  // Class Jaccard
  let classScore = 1.0;
  if (expectedClasses.length > 0 || actualClasses.length > 0) {
    const setA = new Set(expectedClasses);
    const setB = new Set(actualClasses);
    let common = 0;
    for (const c of setA) {
      if (setB.has(c)) common++;
    }
    const union = setA.size + setB.size - common;
    classScore = union === 0 ? 1.0 : common / union;
  }

  // Attributes Jaccard and Levenshtein
  const expectedKeys = Object.keys(expectedAttrs);
  if (expectedKeys.length === 0) {
    return classScore;
  }

  let attrScores: number[] = [];
  for (const key of expectedKeys) {
    const expVal = expectedAttrs[key];
    const actVal = actualAttrs[key];
    if (actVal !== undefined) {
      attrScores.push(normalizedSimilarity(expVal, actVal));
    } else {
      attrScores.push(0.0);
    }
  }

  const avgAttrScore = attrScores.reduce((a, b) => a + b, 0) / attrScores.length;
  return 0.4 * classScore + 0.6 * avgAttrScore;
}

export function fuzzyAttributeMatch(
  expected: Record<string, string>,
  candidate: Record<string, string>,
  threshold: number = 0.75
): boolean {
  const keys = Object.keys(expected);
  if (keys.length === 0) return true;
  let matches = 0;
  for (const k of keys) {
    if (candidate[k] !== undefined && normalizedSimilarity(expected[k], candidate[k]) >= threshold) {
      matches++;
    }
  }
  return (matches / keys.length) >= threshold;
}
