import { apiRequest } from "./client";
import { ApiResult } from "@/lib/types";

export interface UploadResponse {
  id: string;
  project_id: string;
  public_url: string;
  file_name: string;
  upload_status: string;
}

export async function uploadSketch(
  file: File,
  projectId: string,
  token: string
): Promise<ApiResult<UploadResponse>> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_id", projectId);

  return apiRequest<UploadResponse>("/upload", {
    method: "POST",
    body: formData,
    token,
    isFormData: true,
  });
}
