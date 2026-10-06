import { normalizedSimilarity } from '../levenshtein';

export function calculateTextSimilarity(expectedText: string, actualText: string): number {
  if (!expectedText && !actualText) return 1.0;
  if (!expectedText || !actualText) return 0.0;

  const a = expectedText.trim().toLowerCase();
  const b = actualText.trim().toLowerCase();

  if (a === b) return 1.0;

  // Exact substring boost
  if (b.includes(a) || a.includes(b)) {
    const ratio = Math.min(a.length, b.length) / Math.max(a.length, b.length);
    return Math.max(0.85, 0.7 + 0.3 * ratio);
  }

  return normalizedSimilarity(a, b);
}
