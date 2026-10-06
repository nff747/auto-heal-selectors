export * from './types';
export * from './levenshtein';
export * from './tokenizer';
export * from './snapshot/dom_tree';
export * from './snapshot/buffer';
export * from './similarity/structural';
export * from './similarity/attribute';
export * from './similarity/text';
export * from './similarity/composite';
export * from './strategies/base';
export * from './strategies/id_healer';
export * from './strategies/text_healer';
export * from './strategies/aria_healer';
export * from './strategies/hierarchy_healer';
export * from './strategies/proximity_healer';
export * from './engine/confidence';
export * from './engine/pipeline';
export * from './patcher/diff';
export * from './patcher/file_scanner';
export * from './patcher/ast_rewriter';
export * from './storage/healer_store';
export * from './reporters/json_reporter';
export * from './reporters/markdown_reporter';
export * from './reporters/html_reporter';
export * from './adapters/playwright';
export * from './adapters/puppeteer';
export * from './visual/box';
export * from './visual/dom_matrix';
export * from './telemetry/events';
export * from './telemetry/emitter';
export * from './config/loader';
export * from './cli/commands';
export * from './benchmarks/healing_bench';

import { PlaywrightAdapter } from './adapters/playwright';
import { HealerOptions, HealEvent } from './types';
import { tokenizeSelector } from './tokenizer';

export function extractSemanticTokens(selector: string) {
  const t = tokenizeSelector(selector);
  return {
    id: t.id,
    text: t.text,
    role: t.role,
    classes: t.classes
  };
}

export async function withHealer(context: any, options: HealerOptions = {}) {
  const adapter = new PlaywrightAdapter(options);
  return new Proxy(context, {
    get(target, prop, receiver) {
      if (prop === 'newPage') {
        return async (...args: any[]) => {
          const page = await target.newPage(...args);
          return adapter.wrapPage(page);
        };
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}

export function setupPageProxy(page: any, options: HealerOptions = {}) {
  const adapter = new PlaywrightAdapter(options);
  return adapter.wrapPage(page);
}

export function setupLocatorProxy(page: any, originalLocator: any, selector: string, options: HealerOptions = {}) {
  const adapter = new PlaywrightAdapter(options);
  return adapter.wrapLocator(page, originalLocator, selector);
}
