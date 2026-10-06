import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { HealerStore } from '../src/storage/healer_store';

describe('HealerStore', () => {
  const testDir = path.join(__dirname, '.test_healer_store');

  beforeEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(testDir)) fs.rmSync(testDir, { recursive: true });
  });

  it('records events and computes healing success rate', () => {
    const store = new HealerStore(testDir);
    expect(store.getAllEvents().length).toBe(0);
    expect(store.getSuccessRate()).toBe(1.0);

    store.recordEvent({
      originalSelector: '#a',
      healedSelector: '#b',
      strategy: 'id',
      confidence: 0.9,
      action: 'click',
      timestamp: Date.now()
    });

    store.recordEvent({
      originalSelector: '#x',
      healedSelector: '#y',
      strategy: 'text',
      confidence: 0.4,
      action: 'fill',
      timestamp: Date.now()
    });

    expect(store.getAllEvents().length).toBe(2);
    expect(store.getSuccessRate()).toBe(0.5);
  });

  it('recovers gracefully from corrupted store file', () => {
    const store = new HealerStore(testDir);
    fs.writeFileSync(path.join(testDir, 'history.json'), '{ invalid json ...', 'utf-8');
    expect(store.getAllEvents()).toEqual([]);
  });
});
