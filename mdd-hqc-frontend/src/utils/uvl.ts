import type {
  CimToPimUvlPayload,
  TransformationFeature,
  TransformationRestriction,
} from "../types/transformations";

const normaliseName = (value: string): string => {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[^0-9a-zA-Z ]+/g, " ")
    .trim()
    .split(/\s+/)
    .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : ""))
    .join("");
};

const formatFeatureSection = (
  label: string,
  items: TransformationFeature[] = [],
): string[] => {
  if (!items.length) {
    return [];
  }

  const lines: string[] = [`  ${label} {`];
  lines.push(...items.map((feature) => `    ${normaliseName(feature.name)}`));
  lines.push("  }");
  return lines;
};

const formatConstraintsSection = (
  restrictions: TransformationRestriction[] = [],
): string[] => {
  if (!restrictions.length) {
    return [];
  }

  const lines: string[] = ["constraints {"];
  lines.push(
    ...restrictions.map(
      (restriction) => `  ${normaliseName(restriction.name)}`,
    ),
  );
  lines.push("}");
  return lines;
};

export const formatUvlContent = (
  payload?: CimToPimUvlPayload | null,
): string => {
  const lines: string[] = [];
  const features = payload?.features ?? { primary: [], quality: [] };
  const restrictions = payload?.restrictions ?? [];

  lines.push("features {");
  lines.push(...formatFeatureSection("primary", features.primary));
  lines.push(...formatFeatureSection("quality", features.quality));
  lines.push("}");

  const constraintsLines = formatConstraintsSection(restrictions);
  if (constraintsLines.length) {
    lines.push("", ...constraintsLines);
  }

  return lines.join("\n").trim();
};
