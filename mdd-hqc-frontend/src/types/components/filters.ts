import type { LevelKey } from "../levels";

export type LevelFilterProps = {
  from: LevelKey;
  to: LevelKey;
  onFromChange: (value: LevelKey) => void;
  onToChange: (value: LevelKey) => void;
  onTransform: () => void;
  isTransforming?: boolean;
  isTransformDisabled?: boolean;
};
