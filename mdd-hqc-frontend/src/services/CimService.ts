import type { CimToPimTransformationResponse } from "../types/transformations";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const cleanIStarXml = async (xmlContent: string) => {
  const response = await fetch(`${API_BASE_URL}/xml/clean`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: xmlContent }),
  });

  if (!response.ok) {
    throw new Error(`Error cleaning XML: ${response.statusText}`);
  }

  return response.json();
};

export const transformCimToPim = async (
  xmlContent: string,
): Promise<CimToPimTransformationResponse> => {
  const response = await fetch(`${API_BASE_URL}/transformations/cim-to-pim`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ xml_content: xmlContent }),
  });

  if (!response.ok) {
    throw new Error(`Error transforming model: ${response.statusText}`);
  }

  return response.json();
};
