export type ProjectStatus =
  | "draft"
  | "uploading"
  | "analyzing"
  | "spec_ready"
  | "rendering"
  | "render_ready"
  | "techpack_ready"
  | "complete"
  | "error";

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  garment_type?: string;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Upload {
  id: string;
  project_id: string;
  public_url: string;
  file_name: string;
  upload_status: string;
}

export interface Render {
  id: string;
  project_id: string;
  spec_id: string;
  view_type: "front" | "back" | "side_left" | "studio_3q";
  public_url?: string;
  render_status: "queued" | "generating" | "complete" | "error";
}

export interface TechPack {
  id: string;
  project_id: string;
  pdf_url?: string;
  pack_status: string;
}

export interface ProjectFull extends Project {
  uploads?: Upload[];
  garment_specs?: Array<{ id: string; spec_json: Record<string, unknown>; is_current: boolean; version: number }>;
  renders?: Render[];
  techpacks?: TechPack[];
  manufacturing_docs?: Array<{ id: string; doc_status: string }>;
  trend_reports?: Array<{ id: string; report_status: string }>;
  patterns?: Array<{ id: string; piece_name: string; pattern_status: string }>;
}
