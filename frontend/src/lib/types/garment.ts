// TypeScript mirror of backend/app/schemas/garment_spec.py (Pydantic v2 GarmentSpec)

export interface Measurements {
  chest?: number;
  waist?: number;
  hip?: number;
  length?: number;
  sleeve_length?: number;
  shoulder_width?: number;
  unit: string;
}

export interface CollarSpec {
  type?: string;
  height?: number;
  notes?: string;
}

export interface CuffSpec {
  type?: string;
  width?: number;
  closure?: string;
}

export interface ClosureSpec {
  type?: string;
  placement?: string;
  hardware?: string;
  length?: number;
}

export interface PocketSpec {
  type?: string;
  placement?: string;
  dimensions?: Record<string, number>;
}

export interface EmbroiderySpec {
  present: boolean;
  technique?: string;
  placement?: string[];
  thread_colors?: string[];
}

export interface SpecMetadata {
  confidence?: number;
  prompt_version?: string;
  source_type?: string;
  notes?: string;
}

export interface GarmentSpec {
  garment_type: string;
  silhouette: string;
  neckline?: string;
  sleeve_type?: string;
  fit: string;
  panels: string[];
  pockets: PocketSpec[];
  collar?: CollarSpec;
  cuff?: CuffSpec;
  closure?: ClosureSpec;
  trims: string[];
  embroidery?: EmbroiderySpec;
  construction_notes: string[];
  suggested_fabric: string[];
  colors: string[];
  measurements?: Measurements;
  seam_allowance: string;
  metadata: SpecMetadata;
}

export interface GarmentSpecRow {
  id: string;
  project_id: string;
  upload_id?: string;
  user_id: string;
  version: number;
  is_current: boolean;
  garment_type?: string;
  silhouette?: string;
  spec_json: GarmentSpec;
  ai_confidence?: number;
  ai_provider?: string;
  prompt_version?: string;
  created_at: string;
  updated_at: string;
}
