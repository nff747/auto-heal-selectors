export function calculatePathSimilarity(pathA: string[], pathB: string[]): number {
  if (pathA.length === 0 || pathB.length === 0) return 0.0;
  
  // Count matching common suffix elements (elements closest to target node)
  let matchingSuffix = 0;
  const len = Math.min(pathA.length, pathB.length);
  for (let i = 1; i <= len; i++) {
    const elemA = pathA[pathA.length - i];
    const elemB = pathB[pathB.length - i];
    if (elemA.split('#')[0].split('.')[0] === elemB.split('#')[0].split('.')[0]) {
      matchingSuffix++;
    } else {
      break;
    }
  }

  // Jaccard similarity of all ancestors in the chain
  const setA = new Set(pathA);
  const setB = new Set(pathB);
  let intersection = 0;
  for (const item of setA) {
    if (setB.has(item)) intersection++;
  }
  const union = setA.size + setB.size - intersection;
  const jaccard = union === 0 ? 1.0 : intersection / union;

  return 0.6 * (matchingSuffix / len) + 0.4 * jaccard;
}
