import { describe, it, expect } from 'vitest';
import { generateUnifiedDiff } from '../src/patcher/diff';

describe('UnifiedDiffGenerator', () => {
  it('generates standard git-compatible unified diff hunks', () => {
    const diff = generateUnifiedDiff({
      filePath: 'tests/auth.spec.ts',
      originalSelector: '#submit_old_4812',
      healedSelector: '[data-testid="submit_old"]',
      lineNumber: 42
    });

    expect(diff).toContain('--- a/tests/auth.spec.ts');
    expect(diff).toContain('+++ b/tests/auth.spec.ts');
    expect(diff).toContain('@@ -42,1 +42,1 @@');
    expect(diff).toContain("-  await page.locator('#submit_old_4812').click();");
    expect(diff).toContain("+  await page.locator('[data-testid=\"submit_old\"]').click();");
  });
});
