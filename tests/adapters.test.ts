import { describe, it, expect, vi } from 'vitest';
import { PlaywrightAdapter } from '../src/adapters/playwright';
import { PuppeteerAdapter } from '../src/adapters/puppeteer';

describe('browser automation adapters', () => {
  it('PlaywrightAdapter intercepts locator failures and executes action on healed element', async () => {
    const onHeal = vi.fn();
    const adapter = new PlaywrightAdapter({ onHeal });

    const mockPage = {
      locator: (sel: string) => {
        if (sel === '#broken') {
          return {
            click: vi.fn().mockRejectedValue(new Error('Element not found: #broken')),
            count: vi.fn().mockResolvedValue(0)
          };
        }
        return {
          click: vi.fn().mockResolvedValue('clicked_healed'),
          count: vi.fn().mockResolvedValue(1)
        };
      }
    };

    const wrappedPage = adapter.wrapPage(mockPage);
    const loc = wrappedPage.locator('#broken');
    const result = await loc.click();

    expect(result).toBe('clicked_healed');
    expect(onHeal).toHaveBeenCalled();
  });

  it('PuppeteerAdapter heals failing $ query and returns valid element handle', async () => {
    const onHeal = vi.fn();
    const adapter = new PuppeteerAdapter({ onHeal });

    const mockPage = {
      $: vi.fn().mockImplementation(async (sel: string) => {
        if (sel === '#missing') return null;
        return { id: 'element_handle' };
      }),
      $$: vi.fn().mockImplementation(async (sel: string) => {
        if (sel.includes('missing')) return [{ id: 'elem_1' }];
        return [];
      })
    };

    const wrappedPage = adapter.wrapPage(mockPage);
    const element = await wrappedPage.$('#missing');

    expect(element).not.toBeNull();
    expect(onHeal).toHaveBeenCalled();
  });
});
