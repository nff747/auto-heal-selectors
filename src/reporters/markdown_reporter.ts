import { HealEvent } from '../types';

export function generateMarkdownReport(events: HealEvent[]): string {
  if (events.length === 0) {
    return '### 🛡️ Auto-Heal Selectors: 0 Selectors Required Remediation\n\nAll locators matched cleanly during test execution.';
  }

  let md = `### 🤖 Auto-Heal Selectors: Remediation Summary\n\n`;
  md += `| Original Selector | Healed Selector | Strategy | Confidence | Action |\n`;
  md += `| :--- | :--- | :--- | :---: | :---: |\n`;

  for (const e of events) {
    const badge = e.confidence >= 0.8 ? '🟢' : e.confidence >= 0.6 ? '🟡' : '🔴';
    md += `| \`${e.originalSelector}\` | \`${e.healedSelector}\` | ${e.strategy} | ${badge} ${(e.confidence * 100).toFixed(0)}% | \`${e.action}\` |\n`;
  }

  md += `\n*Run \`npx auto-heal patch\` to apply healed locators directly to your test files.*\n`;
  return md;
}
