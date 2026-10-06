import * as fs from 'fs';

export class SourceCodeRewriter {
  public static rewriteSelectorInContent(
    content: string,
    originalSelector: string,
    healedSelector: string
  ): { updatedContent: string; replacements: number } {
    let replacements = 0;
    // Replace inside quotes matching locator('...'), $("..."), etc.
    const escaped = originalSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(['"\`])${escaped}\\1`, 'g');

    const updatedContent = content.replace(regex, (_match, quote) => {
      replacements++;
      return `${quote}${healedSelector}${quote}`;
    });

    return { updatedContent, replacements };
  }

  public static patchFile(
    filePath: string,
    originalSelector: string,
    healedSelector: string
  ): boolean {
    if (!fs.existsSync(filePath)) return false;
    const content = fs.readFileSync(filePath, 'utf-8');
    const { updatedContent, replacements } = this.rewriteSelectorInContent(
      content,
      originalSelector,
      healedSelector
    );
    if (replacements > 0) {
      fs.writeFileSync(filePath, updatedContent, 'utf-8');
      return true;
    }
    return false;
  }
}
