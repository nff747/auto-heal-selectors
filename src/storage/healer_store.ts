import * as fs from 'fs';
import * as path from 'path';
import { HealEvent } from '../types';

export class HealerStore {
  private storeFile: string;

  constructor(storageDir: string = '.healer') {
    this.storeFile = path.join(storageDir, 'history.json');
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
  }

  public recordEvent(event: HealEvent): void {
    const events = this.getAllEvents();
    events.push(event);
    fs.writeFileSync(this.storeFile, JSON.stringify(events, null, 2), 'utf-8');
  }

  public getAllEvents(): HealEvent[] {
    if (!fs.existsSync(this.storeFile)) return [];
    try {
      const data = fs.readFileSync(this.storeFile, 'utf-8');
      return JSON.parse(data);
    } catch {
      return []; // Recover from corrupted store file
    }
  }

  public getSuccessRate(): number {
    const events = this.getAllEvents();
    if (events.length === 0) return 1.0;
    const successful = events.filter(e => e.confidence >= 0.7).length;
    return successful / events.length;
  }
}
