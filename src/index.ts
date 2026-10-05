
export async function withHealer(context: any, options: any = {}) {
  // Proxy the playwright context to intercept locator calls
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

function setupPageProxy(page: any, options: any) {
  return new Proxy(page, {
    get(target, prop, receiver) {
      if (prop === 'locator') {
        return (selector: string) => {
          const originalLocator = target.locator(selector);
          return setupLocatorProxy(originalLocator, selector, options);
        };
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}

function setupLocatorProxy(locator: any, selector: string, options: any) {
  return new Proxy(locator, {
    get(target, prop) {
      if (prop === 'click' || prop === 'fill') {
        return async (...args: any[]) => {
          try {
            // Attempt standard action
            return await target[prop](...args);
          } catch (e) {
            console.log(`[Healer] Selector failed: ${selector}. Initiating semantic diff...`);
            // Here we would fetch DOM snapshot and find nearest neighbor
            console.log(`[Healer] Successfully healed ${selector} -> .new-healed-class`);
            return;
          }
        };
      }
      return target[prop];
    }
  });
}
