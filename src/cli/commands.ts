import * as fs from 'fs';
import * as path from 'path';
import { HealerStore } from '../storage/healer_store';
import { generateMarkdownReport } from '../reporters/markdown_reporter';
import { generateHTMLReport } from '../reporters/html_reporter';
import { generateJSONReport } from '../reporters/json_reporter';
import { SourceCodeRewriter } from '../patcher/ast_rewriter';

export class CLICommands {
  public static report(format: 'markdown' | 'html' | 'json' = 'markdown', dir: string = '.healer'): string {
    const store = new HealerStore(dir);
    const events = store.getAllEvents();

    if (format === 'html') return generateHTMLReport(events);
    if (format === 'json') return generateJSONReport(events);
    return generateMarkdownReport(events);
  }

  public static clean(dir: string = '.healer'): boolean {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true });
      return true;
    }
    return false;
  }

  public static patch(testFilePath: string, originalSelector: string, healedSelector: string): boolean {
    return SourceCodeRewriter.patchFile(testFilePath, originalSelector, healedSelector);
  }
}
