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

os.makedirs(os.path.join(SCRATCH, "src/snapshot"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "src/similarity"), exist_ok=True)

# -------------------------------------------------------------
# Commit 6: feat(snapshot): implement serialized DOM node model
# -------------------------------------------------------------
dom_tree_code = """import { SerializedDOMNode, BoundingBox } from '../types';

export class DOMTreeSnapshot {
  public root: SerializedDOMNode;
  public timestamp: number;

  constructor(root: SerializedDOMNode, timestamp: number = Date.now()) {
    this.root = root;
    this.timestamp = timestamp;
  }

  public findNodes(predicate: (node: SerializedDOMNode) => boolean): SerializedDOMNode[] {
    const results: SerializedDOMNode[] = [];
    const traverse = (node: SerializedDOMNode) => {
      if (predicate(node)) {
        results.push(node);
      }
      if (node.children) {
        for (const child of node.children) {
          traverse(child);
        }
      }
    };
    traverse(this.root);
    return results;
  }

  public findById(id: string): SerializedDOMNode | null {
    const matches = this.findNodes(n => n.id === id || n.attributes?.id === id);
    return matches.length > 0 ? matches[0] : null;
  }

  public getAncestorPath(target: SerializedDOMNode): string[] {
    const path: string[] = [];
    const find = (node: SerializedDOMNode, currentPath: string[]): boolean => {
      const segment = `${node.tagName}${node.id ? '#' + node.id : ''}${node.classes.length > 0 ? '.' + node.classes.join('.') : ''}`;
      const next = [...currentPath, segment];
      if (node === target) {
        path.push(...next);
        return true;
      }
      if (node.children) {
        for (const child of node.children) {
          if (find(child, next)) return true;
        }
      }
      return false;
    };
    find(this.root, []);
    return path;
  }
}
"""
with open(os.path.join(SCRATCH, "src/snapshot/dom_tree.ts"), "w") as f:
    f.write(dom_tree_code)

run_tests()
commit("feat(snapshot): implement serialized DOM node model with geometry and tree hierarchy")

# -------------------------------------------------------------
# Commit 7: feat(snapshot): implement rolling snapshot ring buffer
# -------------------------------------------------------------
buffer_code = """import { DOMTreeSnapshot } from './dom_tree';

export class SnapshotRingBuffer {
  private buffer: DOMTreeSnapshot[] = [];
  private capacity: number;

  constructor(capacity: number = 10) {
    if (capacity <= 0) throw new Error('Capacity must be greater than zero');
    this.capacity = capacity;
  }

  public push(snapshot: DOMTreeSnapshot): void {
    if (this.buffer.length >= this.capacity) {
      this.buffer.shift(); // Evict oldest
    }
    this.buffer.push(snapshot);
  }

  public getLatest(): DOMTreeSnapshot | null {
    return this.buffer.length > 0 ? this.buffer[this.buffer.length - 1] : null;
  }

  public getAll(): readonly DOMTreeSnapshot[] {
    return this.buffer;
  }

  public size(): number {
    return this.buffer.length;
  }

  public clear(): void {
    this.buffer = [];
  }
}
"""
with open(os.path.join(SCRATCH, "src/snapshot/buffer.ts"), "w") as f:
    f.write(buffer_code)

run_tests()
commit("feat(snapshot): implement rolling snapshot ring buffer with capacity management")

# -------------------------------------------------------------
# Commit 8: test(snapshot): add test coverage for DOM snapshotting
# -------------------------------------------------------------
snapshot_test = """import { describe, it, expect } from 'vitest';
import { DOMTreeSnapshot } from '../src/snapshot/dom_tree';
import { SnapshotRingBuffer } from '../src/snapshot/buffer';
import { SerializedDOMNode } from '../src/types';

describe('DOMTreeSnapshot & SnapshotRingBuffer', () => {
  const mockDOM: SerializedDOMNode = {
    tagName: 'body',
    classes: ['theme-dark'],
    attributes: {},
    children: [
      {
        tagName: 'div',
        id: 'main-content',
        classes: ['container'],
        attributes: {},
        children: [
          {
            tagName: 'button',
            id: 'btn-submit',
            classes: ['btn', 'btn-primary'],
            attributes: { type: 'submit' },
            textContent: 'Pay Now'
          }
        ]
      }
    ]
  };

  it('traverses and queries serialized DOM tree nodes', () => {
    const snap = new DOMTreeSnapshot(mockDOM);
    const btn = snap.findById('btn-submit');
    expect(btn).not.toBeNull();
    expect(btn?.tagName).toBe('button');
    expect(btn?.textContent).toBe('Pay Now');

    const path = snap.getAncestorPath(btn!);
    expect(path).toContain('body.theme-dark');
    expect(path[path.length - 1]).toBe('button#btn-submit.btn.btn-primary');
  });

  it('maintains rolling ring buffer with strict capacity enforcement', () => {
    const buffer = new SnapshotRingBuffer(3);
    expect(buffer.size()).toBe(0);

    const s1 = new DOMTreeSnapshot(mockDOM, 100);
    const s2 = new DOMTreeSnapshot(mockDOM, 200);
    const s3 = new DOMTreeSnapshot(mockDOM, 300);
    const s4 = new DOMTreeSnapshot(mockDOM, 400);

    buffer.push(s1);
    buffer.push(s2);
    buffer.push(s3);
    expect(buffer.size()).toBe(3);
    expect(buffer.getLatest()?.timestamp).toBe(300);

    buffer.push(s4); // Should evict s1
    expect(buffer.size()).toBe(3);
    expect(buffer.getAll()[0].timestamp).toBe(200);
    expect(buffer.getLatest()?.timestamp).toBe(400);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/snapshot.test.ts"), "w") as f:
    f.write(snapshot_test)

run_tests()
commit("test(snapshot): add test coverage for DOM snapshotting and ring buffer eviction")

# -------------------------------------------------------------
# Commit 9: feat(similarity): implement structural DOM proximity
# -------------------------------------------------------------
struct_code = """export function calculatePathSimilarity(pathA: string[], pathB: string[]): number {
  if (pathA.length === 0 || pathB.length === 0) return 0.0;
  
  // Count matching common suffix elements (elements closest to target node)
  let matchingSuffix = 0;
  const len = Math.min(pathA.length, pathB.length);
  for (let i = 1; i <= len; i++) {
    const elemA = pathA[pathA.length - i];
    const elemB = pathB[pathB.length - i];
    if (elemA.split('#')[0].split('.')[0] === elemB.split('#')[0].split('.')[0]) {
      matchingSuffix++;
    } else {
      break;
    }
  }

  // Jaccard similarity of all ancestors in the chain
  const setA = new Set(pathA);
  const setB = new Set(pathB);
  let intersection = 0;
  for (const item of setA) {
    if (setB.has(item)) intersection++;
  }
  const union = setA.size + setB.size - intersection;
  const jaccard = union === 0 ? 1.0 : intersection / union;

  return 0.6 * (matchingSuffix / len) + 0.4 * jaccard;
}
"""
with open(os.path.join(SCRATCH, "src/similarity/structural.ts"), "w") as f:
    f.write(struct_code)

run_tests()
commit("feat(similarity): implement structural DOM proximity and ancestor path scoring")

# -------------------------------------------------------------
# Commit 10: feat(similarity): implement multi-attribute Jaccard
# -------------------------------------------------------------
attr_code = """import { normalizedSimilarity } from '../levenshtein';

export function calculateAttributeSimilarity(
  expectedAttrs: Record<string, string>,
  actualAttrs: Record<string, string>,
  expectedClasses: string[],
  actualClasses: string[]
): number {
  // Class Jaccard
  let classScore = 1.0;
  if (expectedClasses.length > 0 || actualClasses.length > 0) {
    const setA = new Set(expectedClasses);
    const setB = new Set(actualClasses);
    let common = 0;
    for (const c of setA) {
      if (setB.has(c)) common++;
    }
    const union = setA.size + setB.size - common;
    classScore = union === 0 ? 1.0 : common / union;
  }

  // Attributes Jaccard and Levenshtein
  const expectedKeys = Object.keys(expectedAttrs);
  if (expectedKeys.length === 0) {
    return classScore;
  }

  let attrScores: number[] = [];
  for (const key of expectedKeys) {
    const expVal = expectedAttrs[key];
    const actVal = actualAttrs[key];
    if (actVal !== undefined) {
      attrScores.push(normalizedSimilarity(expVal, actVal));
    } else {
      attrScores.push(0.0);
    }
  }

  const avgAttrScore = attrScores.reduce((a, b) => a + b, 0) / attrScores.length;
  return 0.4 * classScore + 0.6 * avgAttrScore;
}
"""
with open(os.path.join(SCRATCH, "src/similarity/attribute.ts"), "w") as f:
    f.write(attr_code)

run_tests()
commit("feat(similarity): implement multi-attribute Jaccard and token similarity evaluator")

print("Block 2 (Commits 6-10) completed successfully.")
