export type CimLevelProps = {
  onModelReady: (xml: string) => void;
  onModelCleared?: () => void;
};

export type CimLevelStatus = "idle" | "processing" | "success" | "error";

export type PimLevelProps = {
  content: string;
  isTransforming: boolean;
  errorMessage?: string | null;
};

export type PsmLevelProps = {
  diagramUrl?: string;
  plantUmlSource?: string;
  isTransforming: boolean;
  errorMessage?: string | null;
};
