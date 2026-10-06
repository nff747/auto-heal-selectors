import { HealingPipeline } from '../engine/pipeline';
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
