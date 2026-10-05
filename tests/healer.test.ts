import { describe, it, expect, vi } from 'vitest';
import { withHealer } from '../src/index.js';

describe('auto-heal-selectors engine', () => {
  it('wraps browserContext and intercepts newPage', async () => {
    const mockPage = {
      locator: vi.fn().mockReturnValue({
        click: vi.fn().mockResolvedValue(true)
      })
    };
    const mockContext = {
      newPage: vi.fn().mockResolvedValue(mockPage)
    };

    const healedContext = await withHealer(mockContext);
    const page = await healedContext.newPage();
    expect(page).toBeDefined();

    const loc = page.locator('#login-button');
    await loc.click();
    expect(mockPage.locator).toHaveBeenCalledWith('#login-button');
  });

  it('catches locator failure and triggers healing without throw', async () => {
    const mockPage = {
      locator: vi.fn().mockReturnValue({
        click: vi.fn().mockRejectedValue(new Error('Element not found: #missing'))
      })
    };
    const mockContext = {
      newPage: vi.fn().mockResolvedValue(mockPage)
    };

    const healedContext = await withHealer(mockContext);
    const page = await healedContext.newPage();
    const loc = page.locator('#missing');

    // Should catch and heal gracefully
    await expect(loc.click()).resolves.toBeUndefined();
  });
});
