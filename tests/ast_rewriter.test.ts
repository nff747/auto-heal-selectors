import { describe, it, expect } from 'vitest';
import { SourceCodeRewriter } from '../src/patcher/ast_rewriter';

describe('SourceCodeRewriter', () => {
  it('rewrites selector inside single, double, and backtick quotes', () => {
    const code = `
      await page.locator('#broken_1').click();
      await page.locator("#broken_1").fill("hi");
      await page.locator(\`#broken_1\`).hover();
    `;
    const { updatedContent, replacements } = SourceCodeRewriter.rewriteSelectorInContent(
      code,
      '#broken_1',
      '[data-testid="healed_1"]'
    );

    expect(replacements).toBe(3);
    expect(updatedContent).not.toContain('#broken_1');
    expect(updatedContent).toContain('[data-testid="healed_1"]');
  });

  it('preserves indentation and surrounding syntax untouched', () => {
    const code = '    // Note\n    await page.locator("#btn").click();\n';
    const { updatedContent } = SourceCodeRewriter.rewriteSelectorInContent(code, '#btn', '#healed');
    expect(updatedContent).toBe('    // Note\n    await page.locator("#healed").click();\n');
  });
});
