import { BoundingBox } from '../types';

export interface ViewportOffset {
  scrollX: number;
  scrollY: number;
  zoomFactor?: number;
}

export class DOMMatrixResolver {
  public static toAbsoluteCoordinates(box: BoundingBox, offset: ViewportOffset): BoundingBox {
    const zoom = offset.zoomFactor || 1.0;
    return {
      x: (box.x + offset.scrollX) * zoom,
      y: (box.y + offset.scrollY) * zoom,
      width: box.width * zoom,
      height: box.height * zoom
    };
  }

  public static isWithinViewport(box: BoundingBox, viewportWidth: number, viewportHeight: number): boolean {
    return (
      box.x + box.width > 0 &&
      box.x < viewportWidth &&
      box.y + box.height > 0 &&
      box.y < viewportHeight
    );
  }
}
