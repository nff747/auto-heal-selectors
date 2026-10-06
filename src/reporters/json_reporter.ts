import { HealEvent } from '../types';

export interface JSONReportSummary {
  totalHealed: number;
  averageConfidence: number;
  strategyBreakdown: Record<string, number>;
  events: HealEvent[];
}

export function generateJSONReport(events: HealEvent[]): string {
  const breakdown: Record<string, number> = {};
  let totalConf = 0;

  for (const e of events) {
    breakdown[e.strategy] = (breakdown[e.strategy] || 0) + 1;
    totalConf += e.confidence;
  }

  const summary: JSONReportSummary = {
    totalHealed: events.length,
    averageConfidence: events.length > 0 ? Math.round((totalConf / events.length) * 100) / 100 : 1.0,
    strategyBreakdown: breakdown,
    events
  };

  return JSON.stringify(summary, null, 2);
}
