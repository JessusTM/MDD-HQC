export type LevelKey = "cim" | "pim" | "psm";

export type LevelOption = {
  key: LevelKey;
  label: string;
};

export const levelOptions: LevelOption[] = [
  { key: "cim", label: "i*" },
  { key: "pim", label: "UVL" },
  { key: "psm", label: "Arquitectura" },
];
