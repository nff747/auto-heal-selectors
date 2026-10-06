export interface DiffHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  lines: string[];
}

export function generateUnifiedDiff(params: {
  filePath: string;
  originalSelector: string;
  healedSelector: string;
  lineNumber: number;
  contextLines?: string[];
}): string {
  const lineNo = Math.max(1, params.lineNumber);
  const header = `--- a/${params.filePath}\n+++ b/${params.filePath}`;
  const hunkHeader = `@@ -${lineNo},1 +${lineNo},1 @@`;
  const diffOld = `-  await page.locator('${params.originalSelector}').click();`;
  const diffNew = `+  await page.locator('${params.healedSelector}').click();`;

  return `${header}\n${hunkHeader}\n${diffOld}\n${diffNew}`;
}
