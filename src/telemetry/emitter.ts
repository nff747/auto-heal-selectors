import { HealEvent } from '../types';

export type HealEventListener = (event: HealEvent) => void;

export class TelemetryEmitter {
  private listeners: Set<HealEventListener> = new Set();
  private eventBuffer: HealEvent[] = [];
  private maxBufferSize: number;

  constructor(maxBufferSize: number = 100) {
    this.maxBufferSize = maxBufferSize;
  }

  public subscribe(listener: HealEventListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public emit(event: HealEvent): void {
    if (this.eventBuffer.length >= this.maxBufferSize) {
      this.eventBuffer.shift();
    }
    this.eventBuffer.push(event);

    for (const listener of this.listeners) {
      try {
        listener(event);
      } catch (err) {
        console.error('Error in telemetry listener:', err);
      }
    }
  }

  public flush(): HealEvent[] {
    const events = [...this.eventBuffer];
    this.eventBuffer = [];
    return events;
  }

  public getBufferedEvents(): readonly HealEvent[] {
    return this.eventBuffer;
  }
}
