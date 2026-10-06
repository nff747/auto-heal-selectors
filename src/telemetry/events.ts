import { HealEvent } from '../types';

export interface TelemetryBatch {
  sessionId: string;
  timestamp: number;
  environment: string;
  totalEvents: number;
  events: HealEvent[];
}

export class TelemetryEventFactory {
  public static createBatch(sessionId: string, events: HealEvent[]): TelemetryBatch {
    return {
      sessionId,
      timestamp: Date.now(),
      environment: process.env.NODE_ENV || 'test',
      totalEvents: events.length,
      events
    };
  }
}
