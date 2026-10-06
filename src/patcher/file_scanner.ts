import * as fs from 'fs';
import * as path from 'path';

export interface SelectorCallsite {
  filePath: string;
  lineNumber: number;
  lineContent: string;
  matchedSelector: string;
}

export class TestFileScanner {
  public static scanFile(filePath: string, selector: string): SelectorCallsite[] {
    if (!fs.existsSync(filePath)) return [];
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    const results: SelectorCallsite[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.includes(selector)) {
        results.push({
          filePath,
          lineNumber: i + 1,
          lineContent: line,
          matchedSelector: selector
        });
      }
    }
    return results;
  }
}
