import { HealerOptions } from '../types';

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
