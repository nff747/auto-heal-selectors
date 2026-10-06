import { SerializedDOMNode, BoundingBox } from '../types';

export class DOMTreeSnapshot {
  public root: SerializedDOMNode;
  public timestamp: number;

  constructor(root: SerializedDOMNode, timestamp: number = Date.now()) {
    this.root = root;
    this.timestamp = timestamp;
  }

  public findNodes(predicate: (node: SerializedDOMNode) => boolean): SerializedDOMNode[] {
    const results: SerializedDOMNode[] = [];
    const traverse = (node: SerializedDOMNode) => {
      if (predicate(node)) {
        results.push(node);
      }
      if (node.children) {
        for (const child of node.children) {
          traverse(child);
        }
      }
    };
    traverse(this.root);
    return results;
  }

  public findById(id: string): SerializedDOMNode | null {
    const matches = this.findNodes(n => n.id === id || n.attributes?.id === id);
    return matches.length > 0 ? matches[0] : null;
  }

  public getAncestorPath(target: SerializedDOMNode): string[] {
    const path: string[] = [];
    const find = (node: SerializedDOMNode, currentPath: string[]): boolean => {
      const segment = `${node.tagName}${node.id ? '#' + node.id : ''}${node.classes.length > 0 ? '.' + node.classes.join('.') : ''}`;
      const next = [...currentPath, segment];
      if (node === target) {
        path.push(...next);
        return true;
      }
      if (node.children) {
        for (const child of node.children) {
          if (find(child, next)) return true;
        }
      }
      return false;
    };
    find(this.root, []);
    return path;
  }
}
