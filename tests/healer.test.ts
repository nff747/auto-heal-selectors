import { describe, it, expect, vi } from 'vitest';
import { withHealer, extractSemanticTokens } from '../src/index.js';

describe('auto-heal-selectors engine', () => {
  it('extracts semantic tokens from complex selectors', () => {
    const tokens = extractSemanticTokens('button#submit-order.btn-primary.btn-lg');
    expect(tokens.id).toBe('submit-order');
    expect(tokens.classes).toContain('btn-primary');
    expect(tokens.classes).toContain('btn-lg');
    expect(tokens.role).toBe('button');
  });

  it('transparently executes normal actions when locator succeeds', async () => {
    const mockClick = vi.fn().mockResolvedValue(true);
    const mockPage = {
      locator: vi.fn().mockReturnValue({ click: mockClick })
    };
    const mockContext = { newPage: vi.fn().mockResolvedValue(mockPage) };

    const context = await withHealer(mockContext);
    const page = await context.newPage();
    await page.locator('#btn').click();

    expect(mockClick).toHaveBeenCalled();
  });

  it('heals broken selector and executes the action on the healed element', async () => {
    const healedClick = vi.fn().mockResolvedValue(true);
    const brokenClick = vi.fn().mockRejectedValue(new Error('Element not found'));

    const mockPage = {
      locator: vi.fn((sel: string) => {
        if (sel === '#old-checkout-btn') {
          return { click: brokenClick };
        }
        if (sel.includes('old-checkout-btn')) {
          return {
            count: vi.fn().mockResolvedValue(1),
            first: () => ({ click: healedClick })
          };
        }
        return { count: vi.fn().mockResolvedValue(0) };
      })
    };
    const mockContext = { newPage: vi.fn().mockResolvedValue(mockPage) };

    const healEvents: any[] = [];
    const context = await withHealer(mockContext, {
      onHeal: (event) => healEvents.push(event)
    });

    const page = await context.newPage();
    await page.locator('#old-checkout-btn').click();

    expect(brokenClick).toHaveBeenCalled();
    expect(healedClick).toHaveBeenCalled();
    expect(healEvents.length).toBe(1);
    expect(healEvents[0].originalSelector).toBe('#old-checkout-btn');
    expect(healEvents[0].action).toBe('click');
  });

  it('re-throws original error if no healed candidate exists', async () => {
    const mockPage = {
      locator: vi.fn().mockReturnValue({
        click: vi.fn().mockRejectedValue(new Error('Fatal DOM error')),
        count: vi.fn().mockResolvedValue(0)
      })
    };
    const mockContext = { newPage: vi.fn().mockResolvedValue(mockPage) };

    const context = await withHealer(mockContext);
    const page = await context.newPage();
    await expect(page.locator('#completely-gone').click()).rejects.toThrow('Fatal DOM error');
  });
});
