export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SerializedDOMNode {
  id?: string;
  tagName: string;
  classes: string[];
  attributes: Record<string, string>;
  textContent?: string;
  box?: BoundingBox;
  xpath?: string;
  isVisible?: boolean;
  children?: SerializedDOMNode[];
}

export interface SelectorTokens {
  raw: string;
  id?: string;
  tagName?: string;
  classes: string[];
  attributes: Record<string, string>;
  text?: string;
  role?: string;
  pseudoClasses: string[];
  isXPath: boolean;
}

export interface HealCandidate {
  selector: string;
  strategy: string;
  confidence: number;
  reason: string;
  node?: SerializedDOMNode;
}

export interface HealEvent {
  originalSelector: string;
  healedSelector: string;
  strategy: string;
  confidence: number;
  action: string;
  timestamp: number;
  durationMs?: number;
  testFile?: string;
  lineNumber?: number;
}

export interface HealerOptions {
  autoPatch?: boolean;
  timeoutMs?: number;
  onHeal?: (event: HealEvent) => void;
  confidenceThreshold?: number;
  snapshotBufferSize?: number;
  storageDir?: string;
  weights?: {
    structural?: number;
    attribute?: number;
    text?: number;
  };
}

export interface PatchRecord {
  file: string;
  line: number;
  originalSelector: string;
  healedSelector: string;
  applied: boolean;
  timestamp: number;
}
