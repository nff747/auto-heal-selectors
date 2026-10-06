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

# Ensure clean directory
os.makedirs(os.path.join(SCRATCH, "src"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "tests"), exist_ok=True)

# -------------------------------------------------------------
# Commit 1: feat(types): define comprehensive domain types
# -------------------------------------------------------------
types_code = """export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SerializedDOMNode {
  id?: string;
  tagName: string;
  classes: string[];
  attributes: Record<string, string>;
  textContent?: string;
  box?: BoundingBox;
  xpath?: string;
  isVisible?: boolean;
  children?: SerializedDOMNode[];
}

export interface SelectorTokens {
  raw: string;
  id?: string;
  tagName?: string;
  classes: string[];
  attributes: Record<string, string>;
  text?: string;
  role?: string;
  pseudoClasses: string[];
  isXPath: boolean;
}

export interface HealCandidate {
  selector: string;
  strategy: string;
  confidence: number;
  reason: string;
  node?: SerializedDOMNode;
}

export interface HealEvent {
  originalSelector: string;
  healedSelector: string;
  strategy: string;
  confidence: number;
  action: string;
  timestamp: number;
  durationMs?: number;
  testFile?: string;
  lineNumber?: number;
}

export interface HealerOptions {
  autoPatch?: boolean;
  timeoutMs?: number;
  onHeal?: (event: HealEvent) => void;
  confidenceThreshold?: number;
  snapshotBufferSize?: number;
  storageDir?: string;
  weights?: {
    structural?: number;
    attribute?: number;
    text?: number;
  };
}

export interface PatchRecord {
  file: string;
  line: number;
  originalSelector: string;
  healedSelector: string;
  applied: boolean;
  timestamp: number;
}
"""
with open(os.path.join(SCRATCH, "src/types.ts"), "w") as f:
    f.write(types_code)

run_tests()
commit("feat(types): define comprehensive domain types for DOM nodes, selectors, and healing events")

# -------------------------------------------------------------
# Commit 2: feat(levenshtein): implement fast Levenshtein distance
# -------------------------------------------------------------
lev_code = """export function levenshteinDistance(a: string, b: string): number {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;

  const m = a.length;
  const n = b.length;
  const prevRow = new Array<number>(n + 1);
  const currRow = new Array<number>(n + 1);

  for (let j = 0; j <= n; j++) prevRow[j] = j;

  for (let i = 1; i <= m; i++) {
    currRow[0] = i;
    const aChar = a.charCodeAt(i - 1);
    for (let j = 1; j <= n; j++) {
      const cost = aChar === b.charCodeAt(j - 1) ? 0 : 1;
      currRow[j] = Math.min(
        prevRow[j] + 1,       // deletion
        currRow[j - 1] + 1,   // insertion
        prevRow[j - 1] + cost // substitution
      );
    }
    for (let j = 0; j <= n; j++) {
      prevRow[j] = currRow[j];
    }
  }
  return prevRow[n];
}

export function normalizedSimilarity(a: string, b: string): number {
  const normA = a.trim().toLowerCase();
  const normB = b.trim().toLowerCase();
  if (normA === normB) return 1.0;
  const maxLen = Math.max(normA.length, normB.length);
  if (maxLen === 0) return 1.0;
  const dist = levenshteinDistance(normA, normB);
  return Math.max(0, 1.0 - dist / maxLen);
}
"""
with open(os.path.join(SCRATCH, "src/levenshtein.ts"), "w") as f:
    f.write(lev_code)

run_tests()
commit("feat(levenshtein): implement fast Levenshtein distance and normalized similarity scoring")

# -------------------------------------------------------------
# Commit 3: test(levenshtein): add unit tests for Levenshtein distance
# -------------------------------------------------------------
lev_test = """import { describe, it, expect } from 'vitest';
import { levenshteinDistance, normalizedSimilarity } from '../src/levenshtein';

describe('levenshtein utility', () => {
  it('calculates distance for identical strings', () => {
    expect(levenshteinDistance('submit-button', 'submit-button')).toBe(0);
    expect(normalizedSimilarity('submit-button', 'submit-button')).toBe(1.0);
  });

  it('calculates distance for single insertion and deletion', () => {
    expect(levenshteinDistance('btn', 'btns')).toBe(1);
    expect(levenshteinDistance('button', 'buton')).toBe(1);
  });

  it('handles empty strings gracefully', () => {
    expect(levenshteinDistance('', '')).toBe(0);
    expect(levenshteinDistance('', 'hello')).toBe(5);
    expect(levenshteinDistance('world', '')).toBe(5);
    expect(normalizedSimilarity('', '')).toBe(1.0);
  });

  it('computes normalized case-insensitive similarity ratio', () => {
    const sim = normalizedSimilarity('LoginButton', 'login-button');
    expect(sim).toBeGreaterThan(0.7);
    expect(normalizedSimilarity('submit', 'cancel')).toBeLessThan(0.3);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/levenshtein.test.ts"), "w") as f:
    f.write(lev_test)

run_tests()
commit("test(levenshtein): add unit tests for Levenshtein distance and edge cases")

# -------------------------------------------------------------
# Commit 4: feat(tokenizer): implement multi-syntax selector tokenizer
# -------------------------------------------------------------
tokenizer_code = """import { SelectorTokens } from './types';

export function tokenizeSelector(selector: string): SelectorTokens {
  const raw = selector.trim();
  const tokens: SelectorTokens = {
    raw,
    classes: [],
    attributes: {},
    pseudoClasses: [],
    isXPath: raw.startsWith('//') || raw.startsWith('xpath=')
  };

  if (tokens.isXPath) {
    // Extract ID or text from XPath if present
    const idMatch = raw.match(/@id=['"]([^'"]+)['"]/);
    if (idMatch) tokens.id = idMatch[1];
    const textMatch = raw.match(/contains\\(text\\(\\),\\s*['"]([^'"]+)['"]\\)/);
    if (textMatch) tokens.text = textMatch[1];
    return tokens;
  }

  // Playwright text selector: text="foo" or has-text("foo")
  const textMatch = raw.match(/(?:text=|has-text\\()['"]?([^'"\\)]+)['"]?\\)?/i);
  if (textMatch && textMatch[1]) {
    tokens.text = textMatch[1];
  }

  // Playwright role selector: role=button[name="foo"]
  const roleMatch = raw.match(/role=([a-zA-Z]+)(?:\\[name=['"]([^'"]+)['"]\\])?/i);
  if (roleMatch) {
    tokens.role = roleMatch[1].toLowerCase();
    if (roleMatch[2]) tokens.text = roleMatch[2];
  }

  // Tag name
  const tagMatch = raw.match(/^[a-zA-Z][a-zA-Z0-9]*/);
  if (tagMatch) {
    tokens.tagName = tagMatch[0].toLowerCase();
  }

  // ID: #foo
  const idMatch = raw.match(/#([a-zA-Z0-9_\\-]+)/);
  if (idMatch) {
    tokens.id = idMatch[1];
  }

  // Classes: .foo
  const classMatches = raw.matchAll(/\\.([a-zA-Z0-9_\\-]+)/g);
  for (const m of classMatches) {
    if (m[1]) tokens.classes.push(m[1]);
  }

  // Attributes: [key="value"] or [key*="value"]
  const attrMatches = raw.matchAll(/\\[([a-zA-Z0-9_\\-]+)(?:[*^$]?=['"]?([^'"\\]]+)['"]?)?\\]/g);
  for (const m of attrMatches) {
    const key = m[1];
    const val = m[2] !== undefined ? m[2] : 'true';
    tokens.attributes[key] = val;
  }

  // Pseudo-classes: :nth-child(2), :hover
  const pseudoMatches = raw.matchAll(/:([a-zA-Z0-9_\\-]+(?:\\([^)]+\\))?)/g);
  for (const m of pseudoMatches) {
    if (m[1]) tokens.pseudoClasses.push(m[1]);
  }

  return tokens;
}
"""
with open(os.path.join(SCRATCH, "src/tokenizer.ts"), "w") as f:
    f.write(tokenizer_code)

run_tests()
commit("feat(tokenizer): implement multi-syntax selector tokenizer for CSS and Playwright locators")

# -------------------------------------------------------------
# Commit 5: test(tokenizer): add comprehensive unit tests
# -------------------------------------------------------------
tokenizer_test = """import { describe, it, expect } from 'vitest';
import { tokenizeSelector } from '../src/tokenizer';

describe('selector tokenizer', () => {
  it('parses standard CSS ID and class combinations', () => {
    const tokens = tokenizeSelector('button#submit-btn.btn.primary');
    expect(tokens.tagName).toBe('button');
    expect(tokens.id).toBe('submit-btn');
    expect(tokens.classes).toEqual(['btn', 'primary']);
    expect(tokens.isXPath).toBe(false);
  });

  it('parses attribute selectors and data-testids', () => {
    const tokens = tokenizeSelector('[data-testid="checkout-btn"][aria-disabled="false"]');
    expect(tokens.attributes['data-testid']).toBe('checkout-btn');
    expect(tokens.attributes['aria-disabled']).toBe('false');
  });

  it('parses Playwright text selectors', () => {
    const tokens = tokenizeSelector('button:has-text("Save Changes")');
    expect(tokens.tagName).toBe('button');
    expect(tokens.text).toBe('Save Changes');
  });

  it('parses Playwright role selectors', () => {
    const tokens = tokenizeSelector('role=button[name="Confirm Order"]');
    expect(tokens.role).toBe('button');
    expect(tokens.text).toBe('Confirm Order');
  });

  it('identifies and extracts XPath attributes', () => {
    const tokens = tokenizeSelector('//button[@id="save-action"]');
    expect(tokens.isXPath).toBe(true);
    expect(tokens.id).toBe('save-action');
  });
});
"""
with open(os.path.join(SCRATCH, "tests/tokenizer.test.ts"), "w") as f:
    f.write(tokenizer_test)

run_tests()
commit("test(tokenizer): add comprehensive unit tests for selector parsing and token extraction")

print("Block 1 (Commits 1-5) completed successfully.")
