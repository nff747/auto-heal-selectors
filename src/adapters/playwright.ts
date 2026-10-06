import { HealingPipeline } from '../engine/pipeline';
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
