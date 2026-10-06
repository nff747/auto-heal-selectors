import { describe, it, expect, vi } from 'vitest';
import { TelemetryEmitter } from '../src/telemetry/emitter';
import { TelemetryEventFactory } from '../src/telemetry/events';
import { HealEvent } from '../src/types';

describe('TelemetryEmitter & EventFactory', () => {
  const sampleEvent: HealEvent = {
    originalSelector: '#submit',
    healedSelector: 'button[type="submit"]',
    strategy: 'semantic_role',
    confidence: 0.92,
    action: 'click',
    timestamp: Date.now()
  };

  it('notifies subscribers and tracks buffered events', () => {
    const emitter = new TelemetryEmitter(10);
    const listener = vi.fn();
    const unsubscribe = emitter.subscribe(listener);

    emitter.emit(sampleEvent);
    expect(listener).toHaveBeenCalledWith(sampleEvent);
    expect(emitter.getBufferedEvents().length).toBe(1);

    unsubscribe();
    emitter.emit(sampleEvent);
    expect(listener).toHaveBeenCalledTimes(1);
    expect(emitter.getBufferedEvents().length).toBe(2);
  });

  it('flushes event buffers and constructs telemetry batch payload', () => {
    const emitter = new TelemetryEmitter(10);
    emitter.emit(sampleEvent);

    const flushed = emitter.flush();
    expect(flushed.length).toBe(1);
    expect(emitter.getBufferedEvents().length).toBe(0);

    const batch = TelemetryEventFactory.createBatch('session_123', flushed);
    expect(batch.sessionId).toBe('session_123');
    expect(batch.totalEvents).toBe(1);
  });
});
