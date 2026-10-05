export interface HealerOptions {
  autoPatch?: boolean;
  timeoutMs?: number;
  onHeal?: (event: HealEvent) => void;
  confidenceThreshold?: number;
}

export interface HealEvent {
  originalSelector: string;
  healedSelector: string;
  strategy: string;
  confidence: number;
  action: string;
  timestamp: number;
}

export async function withHealer(context: any, options: HealerOptions = {}) {
  return new Proxy(context, {
    get(target, prop, receiver) {
      if (prop === 'newPage') {
        return async (...args: any[]) => {
          const page = await target.newPage(...args);
          return setupPageProxy(page, options);
        };
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}

export function setupPageProxy(page: any, options: HealerOptions = {}) {
  return new Proxy(page, {
    get(target, prop, receiver) {
      if (prop === 'locator') {
        return (selector: string) => {
          const originalLocator = target.locator(selector);
          return setupLocatorProxy(page, originalLocator, selector, options);
        };
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}

export function extractSemanticTokens(selector: string): {
  id?: string;
  text?: string;
  role?: string;
  classes: string[];
} {
  const tokens: { id?: string; text?: string; role?: string; classes: string[] } = {
    classes: []
  };

  // Match ID (#foo)
  const idMatch = selector.match(/#([a-zA-Z0-9_\-]+)/);
  if (idMatch && idMatch[1]) tokens.id = idMatch[1];

  // Match classes (.foo)
  const classMatches = selector.matchAll(/\.([a-zA-Z0-9_\-]+)/g);
  for (const m of classMatches) {
    if (m[1]) tokens.classes.push(m[1]);
  }

  // Match text= or has-text
  const textMatch = selector.match(/(?:text=|has-text\()['"]?([^'"\)]+)['"]?\)?/i);
  if (textMatch && textMatch[1]) tokens.text = textMatch[1];

  // Match role
  const roleMatch = selector.match(/(button|link|input|heading|checkbox|radio)/i);
  if (roleMatch && roleMatch[1]) tokens.role = roleMatch[1].toLowerCase();

  return tokens;
}

export async function findHealedLocator(page: any, selector: string, options: HealerOptions) {
  const tokens = extractSemanticTokens(selector);
  const candidates: { selector: string; strategy: string; confidence: number }[] = [];

  // Strategy 1: Data-testid or partial ID
  if (tokens.id) {
    candidates.push({
      selector: `[data-testid*="${tokens.id}"], [id*="${tokens.id}"]`,
      strategy: 'id_attribute_match',
      confidence: 0.9
    });
  }

  // Strategy 2: Text matching
  if (tokens.text) {
    candidates.push({
      selector: `text="${tokens.text}"`,
      strategy: 'text_content_match',
      confidence: 0.85
    });
  }

  // Strategy 3: Role with partial class match
  for (const cls of tokens.classes) {
    candidates.push({
      selector: `[class*="${cls}"]`,
      strategy: 'class_substring_match',
      confidence: 0.7
    });
  }

  // Strategy 4: Role fallback
  if (tokens.role) {
    candidates.push({
      selector: `${tokens.role}`,
      strategy: 'semantic_role_fallback',
      confidence: 0.5
    });
  }

  for (const cand of candidates) {
    try {
      const loc = page.locator(cand.selector);
      if (typeof loc.count === 'function') {
        const count = await loc.count();
        if (count > 0) {
          return { locator: loc.first(), ...cand };
        }
      } else {
        return { locator: loc, ...cand };
      }
    } catch {
      continue;
    }
  }

  return null;
}

export function setupLocatorProxy(page: any, originalLocator: any, selector: string, options: HealerOptions) {
  return new Proxy(originalLocator, {
    get(target, prop, receiver) {
      if (['click', 'fill', 'hover', 'check', 'uncheck'].includes(String(prop))) {
        return async (...args: any[]) => {
          try {
            return await target[prop](...args);
          } catch (originalError) {
            const healed = await findHealedLocator(page, selector, options);
            if (healed) {
              const event: HealEvent = {
                originalSelector: selector,
                healedSelector: healed.selector,
                strategy: healed.strategy,
                confidence: healed.confidence,
                action: String(prop),
                timestamp: Date.now()
              };

              if (options.onHeal) {
                options.onHeal(event);
              }

              // Actually execute the action on the healed element!
              return await healed.locator[prop](...args);
            }
            throw originalError;
          }
        };
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}
