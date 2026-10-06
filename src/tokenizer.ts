import { SelectorTokens } from './types';

export function tokenizeSelector(selector: string): SelectorTokens {
  const raw = selector.trim();
  const tokens: SelectorTokens = {
    raw,
    classes: [],
    attributes: {},
    pseudoClasses: [],
    isXPath: raw.startsWith('//') || raw.startsWith('xpath=')
  };

  if (tokens.isXPath) {
    // Extract ID or text from XPath if present
    const idMatch = raw.match(/@id=['"]([^'"]+)['"]/);
    if (idMatch) tokens.id = idMatch[1];
    const textMatch = raw.match(/contains\(text\(\),\s*['"]([^'"]+)['"]\)/);
    if (textMatch) tokens.text = textMatch[1];
    return tokens;
  }

  // Playwright text selector: text="foo" or has-text("foo")
  const textMatch = raw.match(/(?:text=|has-text\()['"]?([^'"\)]+)['"]?\)?/i);
  if (textMatch && textMatch[1]) {
    tokens.text = textMatch[1];
  }

  // Playwright role selector: role=button[name="foo"]
  const roleMatch = raw.match(/role=([a-zA-Z]+)(?:\[name=['"]([^'"]+)['"]\])?/i);
  if (roleMatch) {
    tokens.role = roleMatch[1].toLowerCase();
    if (roleMatch[2]) tokens.text = roleMatch[2];
  }

  // Tag name
  const tagMatch = raw.match(/^[a-zA-Z][a-zA-Z0-9]*/);
  if (tagMatch) {
    tokens.tagName = tagMatch[0].toLowerCase();
  }

  // ID: #foo
  const idMatch = raw.match(/#([a-zA-Z0-9_\-]+)/);
  if (idMatch) {
    tokens.id = idMatch[1];
  }

  // Classes: .foo
  const classMatches = raw.matchAll(/\.([a-zA-Z0-9_\-]+)/g);
  for (const m of classMatches) {
    if (m[1]) tokens.classes.push(m[1]);
  }

  // Attributes: [key="value"] or [key*="value"]
  const attrMatches = raw.matchAll(/\[([a-zA-Z0-9_\-]+)(?:[*^$]?=['"]?([^'"\]]+)['"]?)?\]/g);
  for (const m of attrMatches) {
    const key = m[1];
    const val = m[2] !== undefined ? m[2] : 'true';
    tokens.attributes[key] = val;
  }

  // Pseudo-classes: :nth-child(2), :hover
  const pseudoMatches = raw.matchAll(/:([a-zA-Z0-9_\-]+(?:\([^)]+\))?)/g);
  for (const m of pseudoMatches) {
    if (m[1]) tokens.pseudoClasses.push(m[1]);
  }

  return tokens;
}
