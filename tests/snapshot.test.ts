import { describe, it, expect } from 'vitest';
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
