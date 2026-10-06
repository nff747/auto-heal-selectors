import os
import subprocess
import sys

SCRATCH = "/home/n1khy/.gemini/antigravity/scratch/auto-heal-selectors"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    return res.stdout.strip()

def run_tests():
    res = subprocess.run("npm test", shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print("TESTS FAILED:")
        print(res.stdout)
        print(res.stderr)
        sys.exit(1)
    return True

def commit(msg):
    run_cmd("git add -A")
    out = run_cmd(f'git commit -m "{msg}"')
    print(f"Committed: {msg}")

os.makedirs(os.path.join(SCRATCH, "src/adapters"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "src/visual"), exist_ok=True)

# -------------------------------------------------------------
# Commit 36: feat(adapters): implement native Playwright adapter
# -------------------------------------------------------------
pw_code = r"""import { HealingPipeline } from '../engine/pipeline';
import { HealerOptions, HealEvent } from '../types';

export class PlaywrightAdapter {
  private pipeline: HealingPipeline;
  private options: HealerOptions;

  constructor(options: HealerOptions = {}) {
    this.options = options;
    this.pipeline = new HealingPipeline(options);
  }

  public wrapPage(page: any): any {
    return new Proxy(page, {
      get: (target, prop, receiver) => {
        if (prop === 'locator') {
          return (selector: string) => {
            const originalLocator = target.locator(selector);
            return this.wrapLocator(page, originalLocator, selector);
          };
        }
        return Reflect.get(target, prop, receiver);
      }
    });
  }

  public wrapLocator(page: any, locator: any, originalSelector: string): any {
    const actions = ['click', 'fill', 'hover', 'check', 'uncheck'];
    return new Proxy(locator, {
      get: (target, prop, receiver) => {
        if (actions.includes(String(prop))) {
          return async (...args: any[]) => {
            try {
              return await target[prop](...args);
            } catch (err) {
              const healed = await this.pipeline.evaluate(originalSelector, async (candidateSelector) => {
                const loc = page.locator(candidateSelector);
                const count = typeof loc.count === 'function' ? await loc.count() : 1;
                return { count, element: loc };
              });

              if (healed) {
                const event: HealEvent = {
                  originalSelector,
                  healedSelector: healed.selector,
                  strategy: healed.strategy,
                  confidence: healed.confidence,
                  action: String(prop),
                  timestamp: Date.now()
                };
                if (this.options.onHeal) this.options.onHeal(event);

                const healedLocator = page.locator(healed.selector);
                return await healedLocator[prop](...args);
              }
              throw err;
            }
          };
        }
        return Reflect.get(target, prop, receiver);
      }
    });
  }
}
"""
with open(os.path.join(SCRATCH, "src/adapters/playwright.ts"), "w") as f:
    f.write(pw_code)

run_tests()
commit("feat(adapters): implement native Playwright Page and Locator interceptor adapter")

# -------------------------------------------------------------
# Commit 37: feat(adapters): implement Puppeteer adapter
# -------------------------------------------------------------
pup_code = r"""import { HealingPipeline } from '../engine/pipeline';
import { HealerOptions, HealEvent } from '../types';

export class PuppeteerAdapter {
  private pipeline: HealingPipeline;
  private options: HealerOptions;

  constructor(options: HealerOptions = {}) {
    this.options = options;
    this.pipeline = new HealingPipeline(options);
  }

  public wrapPage(page: any): any {
    return new Proxy(page, {
      get: (target, prop, receiver) => {
        if (prop === '$') {
          return async (selector: string) => {
            try {
              const el = await target.$(selector);
              if (el) return el;
            } catch {}

            const healed = await this.pipeline.evaluate(selector, async (cand) => {
              const els = await target.$$(cand);
              return { count: els ? els.length : 0 };
            });

            if (healed) {
              if (this.options.onHeal) {
                this.options.onHeal({
                  originalSelector: selector,
                  healedSelector: healed.selector,
                  strategy: healed.strategy,
                  confidence: healed.confidence,
                  action: '$',
                  timestamp: Date.now()
                });
              }
              return await target.$(healed.selector);
            }
            return null;
          };
        }
        return Reflect.get(target, prop, receiver);
      }
    });
  }
}
"""
with open(os.path.join(SCRATCH, "src/adapters/puppeteer.ts"), "w") as f:
    f.write(pup_code)

run_tests()
commit("feat(adapters): implement native Puppeteer Page and ElementHandle auto-healing adapter")

# -------------------------------------------------------------
# Commit 38: test(adapters): add test coverage for Playwright and Puppeteer mock adapters
# -------------------------------------------------------------
adapter_test = r"""import { describe, it, expect, vi } from 'vitest';
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
"""
with open(os.path.join(SCRATCH, "tests/adapters.test.ts"), "w") as f:
    f.write(adapter_test)

run_tests()
commit("test(adapters): add test coverage for Playwright and Puppeteer mock adapters")

# -------------------------------------------------------------
# Commit 39: feat(visual): implement 2D bounding box math
# -------------------------------------------------------------
box_code = r"""import { BoundingBox } from '../types';

export class BoundingBoxMath {
  public static area(box: BoundingBox): number {
    return Math.max(0, box.width) * Math.max(0, box.height);
  }

  public static intersection(a: BoundingBox, b: BoundingBox): BoundingBox | null {
    const x1 = Math.max(a.x, b.x);
    const y1 = Math.max(a.y, b.y);
    const x2 = Math.min(a.x + a.width, b.x + b.width);
    const y2 = Math.min(a.y + a.height, b.y + b.height);

    if (x2 <= x1 || y2 <= y1) return null;
    return { x: x1, y: y1, width: x2 - x1, height: y2 - y1 };
  }

  public static intersectionOverUnion(a: BoundingBox, b: BoundingBox): number {
    const inter = this.intersection(a, b);
    if (!inter) return 0.0;
    const interArea = this.area(inter);
    const unionArea = this.area(a) + this.area(b) - interArea;
    return unionArea > 0 ? interArea / unionArea : 0.0;
  }

  public static centerDistance(a: BoundingBox, b: BoundingBox): number {
    const ax = a.x + a.width / 2;
    const ay = a.y + a.height / 2;
    const bx = b.x + b.width / 2;
    const by = b.y + b.height / 2;
    return Math.sqrt((ax - bx) ** 2 + (ay - by) ** 2);
  }
}
"""
with open(os.path.join(SCRATCH, "src/visual/box.ts"), "w") as f:
    f.write(box_code)

run_tests()
commit("feat(visual): implement 2D bounding box math and intersection-over-union metric")

# -------------------------------------------------------------
# Commit 40: feat(visual): implement DOM transform matrix resolver
# -------------------------------------------------------------
matrix_code = r"""import { BoundingBox } from '../types';

export interface ViewportOffset {
  scrollX: number;
  scrollY: number;
  zoomFactor?: number;
}

export class DOMMatrixResolver {
  public static toAbsoluteCoordinates(box: BoundingBox, offset: ViewportOffset): BoundingBox {
    const zoom = offset.zoomFactor || 1.0;
    return {
      x: (box.x + offset.scrollX) * zoom,
      y: (box.y + offset.scrollY) * zoom,
      width: box.width * zoom,
      height: box.height * zoom
    };
  }

  public static isWithinViewport(box: BoundingBox, viewportWidth: number, viewportHeight: number): boolean {
    return (
      box.x + box.width > 0 &&
      box.x < viewportWidth &&
      box.y + box.height > 0 &&
      box.y < viewportHeight
    );
  }
}
"""
with open(os.path.join(SCRATCH, "src/visual/dom_matrix.ts"), "w") as f:
    f.write(matrix_code)

run_tests()
commit("feat(visual): implement DOM transform matrix and scroll offset resolver")

print("Block 8 (Commits 36-40) completed successfully.")
