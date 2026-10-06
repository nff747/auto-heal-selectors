import { describe, it, expect } from 'vitest';
import { calculatePathSimilarity } from '../src/similarity/structural';
import { calculateAttributeSimilarity } from '../src/similarity/attribute';
import { calculateTextSimilarity } from '../src/similarity/text';
import { calculateCompositeSimilarity } from '../src/similarity/composite';

describe('similarity metric engine', () => {
  it('computes path similarity for common DOM structures', () => {
    const pathA = ['html', 'body', 'div#app', 'button.submit'];
    const pathB = ['html', 'body', 'div#app', 'button.submit'];
    expect(calculatePathSimilarity(pathA, pathB)).toBe(1.0);

    const pathC = ['html', 'body', 'section.main', 'button.submit'];
    expect(calculatePathSimilarity(pathA, pathC)).toBeGreaterThan(0.35);
  });

  it('computes attribute and class Jaccard similarity', () => {
    const attrsA = { type: 'button', 'data-action': 'save' };
    const attrsB = { type: 'button', 'data-action': 'save' };
    const score = calculateAttributeSimilarity(attrsA, attrsB, ['btn', 'btn-primary'], ['btn', 'btn-primary']);
    expect(score).toBe(1.0);

    const scorePartial = calculateAttributeSimilarity(attrsA, { type: 'submit' }, ['btn'], ['btn', 'btn-danger']);
    expect(scorePartial).toBeLessThan(0.7);
  });

  it('computes fuzzy and substring text similarity', () => {
    expect(calculateTextSimilarity('Checkout', 'Checkout Now')).toBeGreaterThanOrEqual(0.85);
    expect(calculateTextSimilarity('Sign In', 'Sign Out')).toBeGreaterThan(0.5);
    expect(calculateTextSimilarity('Delete Account', 'Settings')).toBeLessThan(0.4);
  });

  it('evaluates weighted composite similarity', () => {
    const composite = calculateCompositeSimilarity({
      expectedPath: ['body', 'form', 'button'],
      actualPath: ['body', 'form', 'button'],
      expectedAttrs: { type: 'submit' },
      actualAttrs: { type: 'submit' },
      expectedClasses: ['btn'],
      actualClasses: ['btn'],
      expectedText: 'Submit',
      actualText: 'Submit'
    });
    expect(composite).toBe(1.0);
  });
});
