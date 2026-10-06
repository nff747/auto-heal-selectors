# 🤖 auto-heal-selectors

> **Zero-dependency, semantic DOM auto-healer for Playwright and Puppeteer.**
> Heals broken E2E locators in real-time, executes actions transparently, and writes unified diffs back to source code.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-100%25_Passing-brightgreen.svg)]()
[![Performance](https://img.shields.io/badge/Latency-%3C0.05ms-blueviolet.svg)]()

---

## ⚡ The Problem
UI tests and web scrapers are notorious for flakiness. Minor layout changes, dynamic CSS hashes (e.g. CSS Modules, styled-components), or ID regenerations immediately break test suites. Engineering teams waste hundreds of hours manually diagnosing selector failures and updating code.

## 🛡️ The Solution
`auto-heal-selectors` hooks into your browser context's `locator()` calls. When a selector fails:
1. **Pauses failure** and extracts structural, attribute, and text tokens.
2. **Evaluates 5 healing strategies** (Dynamic ID stripper, Semantic text matcher, ARIA role accessibility tree, Hierarchy anchor ancestor, 2D Spatial proximity).
3. **Scores candidates** via composite Levenshtein, Jaccard, and DOM tree edit distance metrics.
4. **Applies ambiguity penalties** to prevent mis-clicks when multiple candidates exist.
5. **Executes the pending action** on the highest-confidence healed element.
6. **Emits telemetry & diffs** to `.healer/` or directly updates your test files.

---

## 🚀 Quick Start

### Installation
```bash
npm install auto-heal-selectors
```

### Playwright Integration
```typescript
import { test, expect } from '@playwright/test';
import { withHealer } from 'auto-heal-selectors';

test('resilient checkout flow', async ({ browser }) => {
  // Wrap context with auto-healer
  const context = await withHealer(await browser.newContext(), {
    autoPatch: true, // Automatically writes healed selectors back to .spec.ts files
    confidenceThreshold: 0.75
  });

  const page = await context.newPage();
  await page.goto('https://shop.example.com');

  // Even if #checkout-btn_99a812 changes to [data-testid="checkout-btn"], this succeeds!
  await page.locator('#checkout-btn_99a812').click();
});
```

---

## 📊 Architecture & Strategy Hierarchy

```
Broken Selector: #submit_btn_a9f812
       │
       ▼
 [ Tokenizer ] ──> Tag: button, ID: submit_btn_a9f812, Classes: []
       │
       ├─► Strategy 1: DynamicIdHealer ─────► [id*="submit_btn"] (Conf: 0.85)
       ├─► Strategy 2: SemanticTextHealer ──► button:has-text("Submit") (Conf: 0.88)
       ├─► Strategy 3: AriaRoleHealer ──────► role=button[name="Submit"] (Conf: 0.90)
       ├─► Strategy 4: HierarchyAnchor ─────► form.checkout >> button (Conf: 0.70)
       └─► Strategy 5: SpatialProximity ────► text="Cart Total" >> xpath=..//button (Conf: 0.65)
       │
       ▼
 [ Confidence & Ambiguity Evaluator ]
       │  (Count = 1 -> Uniqueness Bonus +0.05)
       ▼
 Winner: role=button[name="Submit"] (Score: 0.95)
       │
       ├─► Execute pending action transparently
       ├─► Record event to .healer/history.json
       └─► Generate Git Unified Diff for Source Code
```

---

## 🛠️ CLI Usage

```bash
# Generate Markdown report for GitHub Step Summary
npx auto-heal report --format markdown

# Generate Interactive HTML dashboard
npx auto-heal report --format html > .healer/report.html

# Apply healed selectors to test source files
npx auto-heal patch tests/checkout.spec.ts '#submit_btn_a9f812' 'role=button[name="Submit"]'

# Clean local healer artifacts
npx auto-heal clean
```

---

## 🧪 Testing & Verification
```bash
npm test
```
All 15 test suites and 40+ unit/integration tests pass with sub-millisecond execution times.

---

## 📄 License
Licensed under the [Apache License, Version 2.0](LICENSE).
