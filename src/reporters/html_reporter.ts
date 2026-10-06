import { HealEvent } from '../types';

export function generateHTMLReport(events: HealEvent[]): string {
  const rows = events.map(e => `
    <tr>
      <td class="code">${escapeHtml(e.originalSelector)}</td>
      <td class="code healed">${escapeHtml(e.healedSelector)}</td>
      <td><span class="badge strategy">${escapeHtml(e.strategy)}</span></td>
      <td><span class="badge ${e.confidence >= 0.8 ? 'high' : 'med'}">${(e.confidence * 100).toFixed(0)}%</span></td>
      <td><code>${escapeHtml(e.action)}</code></td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Auto-Heal Selectors Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }
    h1 { color: #58a6ff; font-size: 1.5rem; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: #161b22; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #30363d; }
    th { background: #21262d; color: #8b949e; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
    .code { font-family: monospace; font-size: 0.9rem; }
    .healed { color: #3fb950; font-weight: bold; }
    .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge.high { background: #238636; color: white; }
    .badge.med { background: #d29922; color: black; }
    .badge.strategy { background: #388bfd33; color: #58a6ff; }
  </style>
</head>
<body>
  <h1>🛡️ Auto-Heal Selectors Telemetry Report</h1>
  <p>Total Elements Remediated: <strong>${events.length}</strong></p>
  <table>
    <thead>
      <tr>
        <th>Broken Selector</th>
        <th>Healed Replacement</th>
        <th>Strategy</th>
        <th>Confidence</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      ${rows}
    </tbody>
  </table>
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
