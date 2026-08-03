-- Additional indexes for performance
-- Core indexes are already in schema.sql; add any future ones here

-- JSONB spec field lookups
CREATE INDEX IF NOT EXISTS idx_garment_specs_garment_type
    ON public.garment_specs((spec_json->>'garment_type'));

CREATE INDEX IF NOT EXISTS idx_garment_specs_silhouette
    ON public.garment_specs((spec_json->>'silhouette'));

-- Project dashboard ordering
CREATE INDEX IF NOT EXISTS idx_projects_user_updated
    ON public.projects(user_id, updated_at DESC);
