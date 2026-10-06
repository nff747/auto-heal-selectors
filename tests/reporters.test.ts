import { describe, it, expect } from 'vitest';
import { generateJSONReport } from '../src/reporters/json_reporter';
import { generateMarkdownReport } from '../src/reporters/markdown_reporter';
import { generateHTMLReport } from '../src/reporters/html_reporter';
import { HealEvent } from '../src/types';

describe('telemetry reporters', () => {
  const events: HealEvent[] = [
    {
      originalSelector: '#submit_old',
      healedSelector: '[data-testid="submit_new"]',
      strategy: 'dynamic_id_attribute',
      confidence: 0.9,
      action: 'click',
      timestamp: Date.now()
    }
  ];

  it('generates structured JSON summary with metrics', () => {
    const jsonStr = generateJSONReport(events);
    const parsed = JSON.parse(jsonStr);
    expect(parsed.totalHealed).toBe(1);
    expect(parsed.averageConfidence).toBe(0.9);
    expect(parsed.strategyBreakdown['dynamic_id_attribute']).toBe(1);
  });

  it('generates Markdown summary table', () => {
    const md = generateMarkdownReport(events);
    expect(md).toContain('| `#submit_old` | `[data-testid="submit_new"]` |');
    expect(md).toContain('90%');
  });

  it('generates HTML report document with escaped content', () => {
    const html = generateHTMLReport(events);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('#submit_old');
    expect(html).toContain('[data-testid=&quot;submit_new&quot;]');
  });
});
