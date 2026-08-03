import { apiRequest } from "./client";
import { ApiResult, GarmentSpecRow } from "@/lib/types";

export function analyzeSketch(
  uploadId: string,
  projectId: string,
  token: string,
  userNotes?: string
): Promise<ApiResult<GarmentSpecRow>> {
  return apiRequest<GarmentSpecRow>("/vision/analyze", {
    method: "POST",
    body: { upload_id: uploadId, project_id: projectId, user_notes: userNotes ?? "" },
    token,
  });
}

export function getSpec(specId: string, token: string): Promise<ApiResult<GarmentSpecRow>> {
  return apiRequest<GarmentSpecRow>(`/vision/spec/${specId}`, { method: "GET", token });
}

export function updateSpec(
  specId: string,
  updates: Record<string, unknown>,
  token: string
): Promise<ApiResult<GarmentSpecRow>> {
  return apiRequest<GarmentSpecRow>(`/vision/spec/${specId}`, {
    method: "PATCH",
    body: updates,
    token,
  });
}
