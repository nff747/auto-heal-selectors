import { DOMTreeSnapshot } from './dom_tree';

export class SnapshotRingBuffer {
  private buffer: DOMTreeSnapshot[] = [];
  private capacity: number;

  constructor(capacity: number = 10) {
    if (capacity <= 0) throw new Error('Capacity must be greater than zero');
    this.capacity = capacity;
  }

  public push(snapshot: DOMTreeSnapshot): void {
    if (this.buffer.length >= this.capacity) {
      this.buffer.shift(); // Evict oldest
    }
    this.buffer.push(snapshot);
  }

  public getLatest(): DOMTreeSnapshot | null {
    return this.buffer.length > 0 ? this.buffer[this.buffer.length - 1] : null;
  }

  public getAll(): readonly DOMTreeSnapshot[] {
    return this.buffer;
  }

  public size(): number {
    return this.buffer.length;
  }

  public clear(): void {
    this.buffer = [];
  }
}
