import { BoundingBox } from '../types';

export class BoundingBoxMath {
  public static area(box: BoundingBox): number {
    return Math.max(0, box.width) * Math.max(0, box.height);
  }

  public static intersection(a: BoundingBox, b: BoundingBox): BoundingBox | null {
    const x1 = Math.max(a.x, b.x);
    const y1 = Math.max(a.y, b.y);
    const x2 = Math.min(a.x + a.width, b.x + b.width);
    const y2 = Math.min(a.y + a.height, b.y + b.height);

    if (x2 <= x1 || y2 <= y1) return null;
    return { x: x1, y: y1, width: x2 - x1, height: y2 - y1 };
  }

  public static intersectionOverUnion(a: BoundingBox, b: BoundingBox): number {
    const inter = this.intersection(a, b);
    if (!inter) return 0.0;
    const interArea = this.area(inter);
    const unionArea = this.area(a) + this.area(b) - interArea;
    return unionArea > 0 ? interArea / unionArea : 0.0;
  }

  public static centerDistance(a: BoundingBox, b: BoundingBox): number {
    const ax = a.x + a.width / 2;
    const ay = a.y + a.height / 2;
    const bx = b.x + b.width / 2;
    const by = b.y + b.height / 2;
    return Math.sqrt((ax - bx) ** 2 + (ay - by) ** 2);
  }
}
