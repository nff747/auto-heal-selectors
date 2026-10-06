import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { TestFileScanner } from '../src/patcher/file_scanner';

describe('TestFileScanner', () => {
  const tempFile = path.join(__dirname, 'temp_test_spec.ts');

  beforeEach(() => {
    fs.writeFileSync(tempFile, "import { test } from '@playwright/test';\ntest('login', async ({ page }) => {\n  await page.locator('#broken_btn').click();\n});\n");
  });

  afterEach(() => {
    if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
  });

  it('scans file and locates line number containing the target selector', () => {
    const results = TestFileScanner.scanFile(tempFile, '#broken_btn');
    expect(results.length).toBe(1);
    expect(results[0].lineNumber).toBe(3);
    expect(results[0].lineContent).toContain('#broken_btn');
  });

  it('returns empty array if selector is not present', () => {
    const results = TestFileScanner.scanFile(tempFile, '#non_existent');
    expect(results.length).toBe(0);
  });
});
