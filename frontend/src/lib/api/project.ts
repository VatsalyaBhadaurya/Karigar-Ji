import { apiRequest } from "./client";
import { ApiResult, Project, ProjectFull } from "@/lib/types";

export function createProject(
  name: string,
  description: string,
  token: string
): Promise<ApiResult<Project>> {
  return apiRequest<Project>("/project", {
    method: "POST",
    body: { name, description },
    token,
  });
}

export function listProjects(token: string): Promise<ApiResult<Project[]>> {
  return apiRequest<Project[]>("/project", { method: "GET", token });
}

export function getProject(projectId: string, token: string): Promise<ApiResult<ProjectFull>> {
  return apiRequest<ProjectFull>(`/project/${projectId}`, { method: "GET", token });
}

export function updateProject(
  projectId: string,
  updates: Partial<Pick<Project, "name" | "description" | "status">>,
  token: string
): Promise<ApiResult<Project>> {
  return apiRequest<Project>(`/project/${projectId}`, {
    method: "PATCH",
    body: updates as Record<string, unknown>,
    token,
  });
}
