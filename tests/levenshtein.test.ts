import { describe, it, expect } from 'vitest';
import { levenshteinDistance, normalizedSimilarity } from '../src/levenshtein';

describe('levenshtein utility', () => {
  it('calculates distance for identical strings', () => {
    expect(levenshteinDistance('submit-button', 'submit-button')).toBe(0);
    expect(normalizedSimilarity('submit-button', 'submit-button')).toBe(1.0);
  });

  it('calculates distance for single insertion and deletion', () => {
    expect(levenshteinDistance('btn', 'btns')).toBe(1);
    expect(levenshteinDistance('button', 'buton')).toBe(1);
  });

  it('handles empty strings gracefully', () => {
    expect(levenshteinDistance('', '')).toBe(0);
    expect(levenshteinDistance('', 'hello')).toBe(5);
    expect(levenshteinDistance('world', '')).toBe(5);
    expect(normalizedSimilarity('', '')).toBe(1.0);
  });

  it('computes normalized case-insensitive similarity ratio', () => {
    const sim = normalizedSimilarity('LoginButton', 'login-button');
    expect(sim).toBeGreaterThan(0.7);
    expect(normalizedSimilarity('submit', 'cancel')).toBeLessThan(0.3);
  });
});
