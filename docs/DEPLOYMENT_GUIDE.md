# Production Deployment & Embed Guide // Auto Heal Selectors

## 1. Browser Native & Web Worker Environment
Install via your preferred package manager:
```bash
npm install auto-heal-selectors
```

```javascript
import { EngineContext } from 'auto-heal-selectors';

const engine = new EngineContext({
  arenaSize: 32 * 1024 * 1024,
  strictMode: true
});

await engine.initialize();
```

## 2. Air-Gapped / Sovereign Deployments
Download the zero-dependency bundle or clone directly. No external registry or network access is required at runtime.
