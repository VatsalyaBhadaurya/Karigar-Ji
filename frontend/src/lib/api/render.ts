import { apiRequest } from "./client";
import { ApiResult, Render } from "@/lib/types";

export function createRenders(
  specId: string,
  projectId: string,
  token: string,
  views?: string[]
): Promise<ApiResult<{ renders: Render[]; message: string }>> {
  return apiRequest("/render", {
    method: "POST",
    body: {
      spec_id: specId,
      project_id: projectId,
      views: views ?? ["front", "back", "side_left", "studio_3q"],
    },
    token,
  });
}

export function getRender(renderId: string, token: string): Promise<ApiResult<Render>> {
  return apiRequest<Render>(`/render/${renderId}`, { method: "GET", token });
}

export function retryRender(renderId: string, token: string): Promise<ApiResult<Render>> {
  return apiRequest<Render>(`/render/${renderId}/retry`, { method: "POST", token });
}
