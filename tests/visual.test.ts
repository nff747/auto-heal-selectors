import { describe, it, expect } from 'vitest';
import { BoundingBoxMath } from '../src/visual/box';
import { DOMMatrixResolver } from '../src/visual/dom_matrix';

describe('visual geometry calculations', () => {
  it('calculates bounding box area and intersection over union', () => {
    const boxA = { x: 0, y: 0, width: 100, height: 100 };
    const boxB = { x: 50, y: 0, width: 100, height: 100 };

    expect(BoundingBoxMath.area(boxA)).toBe(10000);

    const inter = BoundingBoxMath.intersection(boxA, boxB);
    expect(inter).not.toBeNull();
    expect(inter?.width).toBe(50);
    expect(inter?.height).toBe(100);

    const iou = BoundingBoxMath.intersectionOverUnion(boxA, boxB);
    expect(iou).toBeCloseTo(5000 / 15000, 2);
  });

  it('calculates Euclidean center distance between elements', () => {
    const boxA = { x: 0, y: 0, width: 20, height: 20 }; // Center (10, 10)
    const boxB = { x: 30, y: 40, width: 20, height: 20 }; // Center (40, 50)
    // Distance = sqrt(30^2 + 40^2) = 50
    expect(BoundingBoxMath.centerDistance(boxA, boxB)).toBe(50);
  });

  it('transforms bounding box with viewport offsets and evaluates visibility', () => {
    const box = { x: 10, y: 20, width: 100, height: 50 };
    const absolute = DOMMatrixResolver.toAbsoluteCoordinates(box, { scrollX: 50, scrollY: 100, zoomFactor: 1.0 });

    expect(absolute.x).toBe(60);
    expect(absolute.y).toBe(120);

    expect(DOMMatrixResolver.isWithinViewport(box, 1920, 1080)).toBe(true);
    expect(DOMMatrixResolver.isWithinViewport({ x: -200, y: 0, width: 50, height: 50 }, 1920, 1080)).toBe(false);
  });
});
