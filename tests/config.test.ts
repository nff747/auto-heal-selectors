import { describe, it, expect } from 'vitest';
import { ConfigLoader, DEFAULT_CONFIG } from '../src/config/loader';

describe('ConfigLoader', () => {
  it('applies default configuration when no options passed', () => {
    const config = ConfigLoader.resolveConfig();
    expect(config.confidenceThreshold).toBe(DEFAULT_CONFIG.confidenceThreshold);
    expect(config.autoPatch).toBe(false);
    expect(config.storageDir).toBe('.healer');
  });

  it('overrides defaults with user options', () => {
    const config = ConfigLoader.resolveConfig({
      confidenceThreshold: 0.85,
      autoPatch: true
    });
    expect(config.confidenceThreshold).toBe(0.85);
    expect(config.autoPatch).toBe(true);
  });
});
