import os
import subprocess
import sys

SCRATCH = "/home/n1khy/.gemini/antigravity/scratch/auto-heal-selectors"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    return res.stdout.strip()

def run_tests():
    res = subprocess.run("npm test", shell=True, cwd=SCRATCH, capture_output=True, text=True)
    if res.returncode != 0:
        print("TESTS FAILED:")
        print(res.stdout)
        print(res.stderr)
        sys.exit(1)
    return True

def commit(msg):
    run_cmd("git add -A")
    out = run_cmd(f'git commit -m "{msg}"')
    print(f"Committed: {msg}")

os.makedirs(os.path.join(SCRATCH, "src/telemetry"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "src/config"), exist_ok=True)

# -------------------------------------------------------------
# Commit 41: test(visual): add tests for bounding box calculations
# -------------------------------------------------------------
visual_test = r"""import { describe, it, expect } from 'vitest';
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
"""
with open(os.path.join(SCRATCH, "tests/visual.test.ts"), "w") as f:
    f.write(visual_test)

run_tests()
commit("test(visual): add tests for bounding box calculations and coordinate transformations")

# -------------------------------------------------------------
# Commit 42: feat(telemetry): implement structured event schemas
# -------------------------------------------------------------
events_code = r"""import { HealEvent } from '../types';

export interface TelemetryBatch {
  sessionId: string;
  timestamp: number;
  environment: string;
  totalEvents: number;
  events: HealEvent[];
}

export class TelemetryEventFactory {
  public static createBatch(sessionId: string, events: HealEvent[]): TelemetryBatch {
    return {
      sessionId,
      timestamp: Date.now(),
      environment: process.env.NODE_ENV || 'test',
      totalEvents: events.length,
      events
    };
  }
}
"""
with open(os.path.join(SCRATCH, "src/telemetry/events.ts"), "w") as f:
    f.write(events_code)

run_tests()
commit("feat(telemetry): implement structured event schemas and remediation metrics")

# -------------------------------------------------------------
# Commit 43: feat(telemetry): implement asynchronous event emitter
# -------------------------------------------------------------
emitter_code = r"""import { HealEvent } from '../types';

export type HealEventListener = (event: HealEvent) => void;

export class TelemetryEmitter {
  private listeners: Set<HealEventListener> = new Set();
  private eventBuffer: HealEvent[] = [];
  private maxBufferSize: number;

  constructor(maxBufferSize: number = 100) {
    this.maxBufferSize = maxBufferSize;
  }

  public subscribe(listener: HealEventListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public emit(event: HealEvent): void {
    if (this.eventBuffer.length >= this.maxBufferSize) {
      this.eventBuffer.shift();
    }
    this.eventBuffer.push(event);

    for (const listener of this.listeners) {
      try {
        listener(event);
      } catch (err) {
        console.error('Error in telemetry listener:', err);
      }
    }
  }

  public flush(): HealEvent[] {
    const events = [...this.eventBuffer];
    this.eventBuffer = [];
    return events;
  }

  public getBufferedEvents(): readonly HealEvent[] {
    return this.eventBuffer;
  }
}
"""
with open(os.path.join(SCRATCH, "src/telemetry/emitter.ts"), "w") as f:
    f.write(emitter_code)

run_tests()
commit("feat(telemetry): implement asynchronous event emitter with batch flushing")

# -------------------------------------------------------------
# Commit 44: test(telemetry): add tests for telemetry emission
# -------------------------------------------------------------
telemetry_test = r"""import { describe, it, expect, vi } from 'vitest';
import { TelemetryEmitter } from '../src/telemetry/emitter';
import { TelemetryEventFactory } from '../src/telemetry/events';
import { HealEvent } from '../src/types';

describe('TelemetryEmitter & EventFactory', () => {
  const sampleEvent: HealEvent = {
    originalSelector: '#submit',
    healedSelector: 'button[type="submit"]',
    strategy: 'semantic_role',
    confidence: 0.92,
    action: 'click',
    timestamp: Date.now()
  };

  it('notifies subscribers and tracks buffered events', () => {
    const emitter = new TelemetryEmitter(10);
    const listener = vi.fn();
    const unsubscribe = emitter.subscribe(listener);

    emitter.emit(sampleEvent);
    expect(listener).toHaveBeenCalledWith(sampleEvent);
    expect(emitter.getBufferedEvents().length).toBe(1);

    unsubscribe();
    emitter.emit(sampleEvent);
    expect(listener).toHaveBeenCalledTimes(1);
    expect(emitter.getBufferedEvents().length).toBe(2);
  });

  it('flushes event buffers and constructs telemetry batch payload', () => {
    const emitter = new TelemetryEmitter(10);
    emitter.emit(sampleEvent);

    const flushed = emitter.flush();
    expect(flushed.length).toBe(1);
    expect(emitter.getBufferedEvents().length).toBe(0);

    const batch = TelemetryEventFactory.createBatch('session_123', flushed);
    expect(batch.sessionId).toBe('session_123');
    expect(batch.totalEvents).toBe(1);
  });
});
"""
with open(os.path.join(SCRATCH, "tests/telemetry.test.ts"), "w") as f:
    f.write(telemetry_test)

run_tests()
commit("test(telemetry): add tests for telemetry emission, buffering, and event listeners")

# -------------------------------------------------------------
# Commit 45: feat(config): implement configuration loader
# -------------------------------------------------------------
config_code = r"""import { HealerOptions } from '../types';

export const DEFAULT_CONFIG: HealerOptions = {
  autoPatch: false,
  timeoutMs: 5000,
  confidenceThreshold: 0.65,
  snapshotBufferSize: 10,
  storageDir: '.healer',
  weights: {
    structural: 0.3,
    attribute: 0.4,
    text: 0.3
  }
};

export class ConfigLoader {
  public static resolveConfig(userOptions: Partial<HealerOptions> = {}): HealerOptions {
    const envThreshold = process.env.AUTO_HEAL_THRESHOLD 
      ? parseFloat(process.env.AUTO_HEAL_THRESHOLD) 
      : undefined;

    const envAutoPatch = process.env.AUTO_HEAL_AUTOPATCH 
      ? process.env.AUTO_HEAL_AUTOPATCH === 'true' 
      : undefined;

    return {
      ...DEFAULT_CONFIG,
      ...userOptions,
      confidenceThreshold: userOptions.confidenceThreshold ?? envThreshold ?? DEFAULT_CONFIG.confidenceThreshold,
      autoPatch: userOptions.autoPatch ?? envAutoPatch ?? DEFAULT_CONFIG.autoPatch,
      weights: {
        ...DEFAULT_CONFIG.weights,
        ...userOptions.weights
      }
    };
  }
}
"""
with open(os.path.join(SCRATCH, "src/config/loader.ts"), "w") as f:
    f.write(config_code)

run_tests()
commit("feat(config): implement configuration loader with defaults and env var support")

print("Block 9 (Commits 41-45) completed successfully.")
