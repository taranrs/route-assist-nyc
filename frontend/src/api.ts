import type { CompareRoutesRequest, CompareRoutesResponse } from "./types";

export async function compareRoutesRequest(
  payload: CompareRoutesRequest
): Promise<CompareRoutesResponse> {
  const response = await fetch("/api/routes/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Route comparison failed.");
  }

  return response.json() as Promise<CompareRoutesResponse>;
}
