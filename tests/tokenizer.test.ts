import { describe, it, expect } from 'vitest';
import { tokenizeSelector } from '../src/tokenizer';

describe('selector tokenizer', () => {
  it('parses standard CSS ID and class combinations', () => {
    const tokens = tokenizeSelector('button#submit-btn.btn.primary');
    expect(tokens.tagName).toBe('button');
    expect(tokens.id).toBe('submit-btn');
    expect(tokens.classes).toEqual(['btn', 'primary']);
    expect(tokens.isXPath).toBe(false);
  });

  it('parses attribute selectors and data-testids', () => {
    const tokens = tokenizeSelector('[data-testid="checkout-btn"][aria-disabled="false"]');
    expect(tokens.attributes['data-testid']).toBe('checkout-btn');
    expect(tokens.attributes['aria-disabled']).toBe('false');
  });

  it('parses Playwright text selectors', () => {
    const tokens = tokenizeSelector('button:has-text("Save Changes")');
    expect(tokens.tagName).toBe('button');
    expect(tokens.text).toBe('Save Changes');
  });

  it('parses Playwright role selectors', () => {
    const tokens = tokenizeSelector('role=button[name="Confirm Order"]');
    expect(tokens.role).toBe('button');
    expect(tokens.text).toBe('Confirm Order');
  });

  it('identifies and extracts XPath attributes', () => {
    const tokens = tokenizeSelector('//button[@id="save-action"]');
    expect(tokens.isXPath).toBe(true);
    expect(tokens.id).toBe('save-action');
  });
});
