import type { PimToPsmContextMetrics, PimToPsmResponse } from "../types/transformations";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const transformPimToPsm = async (
  uvlContent: string,
  contextMetrics?: PimToPsmContextMetrics | null,
): Promise<PimToPsmResponse> => {
  const response = await fetch(`${API_BASE_URL}/transformations/pim-to-psm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      uvl_content: uvlContent,
      context_metrics: contextMetrics ?? null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Error transforming UVL: ${response.statusText}`);
  }

  return response.json();
};
