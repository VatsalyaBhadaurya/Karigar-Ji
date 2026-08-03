-- KarigarJi Database Schema
-- Run in Supabase SQL Editor or via psql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- PROFILES (extends Supabase auth.users)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email           TEXT NOT NULL,
    full_name       TEXT,
    avatar_url      TEXT,
    locale          TEXT NOT NULL DEFAULT 'en' CHECK (locale IN ('en', 'hi')),
    plan            TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- PROJECTS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
                        'draft', 'uploading', 'analyzing', 'spec_ready',
                        'rendering', 'render_ready', 'techpack_ready', 'complete', 'error'
                    )),
    garment_type    TEXT,
    thumbnail_url   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status  ON public.projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created ON public.projects(created_at DESC);

-- ============================================================
-- UPLOADS (raw sketch files in Supabase Storage)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.uploads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    storage_path    TEXT NOT NULL,
    public_url      TEXT NOT NULL,
    file_name       TEXT NOT NULL,
    file_size       INTEGER,
    mime_type       TEXT,
    upload_status   TEXT NOT NULL DEFAULT 'pending' CHECK (upload_status IN ('pending', 'processing', 'complete', 'error')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uploads_project_id ON public.uploads(project_id);

-- ============================================================
-- GARMENT SPECS — SINGLE SOURCE OF TRUTH
-- ============================================================
CREATE TABLE IF NOT EXISTS public.garment_specs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    upload_id           UUID REFERENCES public.uploads(id),
    user_id             UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    version             INTEGER NOT NULL DEFAULT 1,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,

    -- Denormalized fast-access columns
    garment_type        TEXT,
    silhouette          TEXT,
    neckline            TEXT,
    sleeve_type         TEXT,
    fit                 TEXT,

    -- Full spec as JSONB
    spec_json           JSONB NOT NULL,

    -- AI metadata
    ai_confidence       FLOAT CHECK (ai_confidence BETWEEN 0.0 AND 1.0),
    ai_provider         TEXT DEFAULT 'gemini-2.5-flash',
    ai_model_version    TEXT,
    prompt_version      TEXT,
    raw_ai_response     JSONB,
    validation_errors   JSONB,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_garment_specs_project_id ON public.garment_specs(project_id);
CREATE INDEX IF NOT EXISTS idx_garment_specs_spec_json  ON public.garment_specs USING gin(spec_json);

-- Only one current spec per project
CREATE UNIQUE INDEX IF NOT EXISTS idx_garment_specs_current
    ON public.garment_specs(project_id)
    WHERE is_current = TRUE;

-- ============================================================
-- RENDERS (FLUX Kontext / fal.ai outputs)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.renders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id         UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    view_type       TEXT NOT NULL CHECK (view_type IN ('front', 'back', 'side_left', 'side_right', 'studio_3q', 'detail')),
    storage_path    TEXT,
    public_url      TEXT,
    render_status   TEXT NOT NULL DEFAULT 'queued' CHECK (render_status IN ('queued', 'generating', 'complete', 'error')),
    fal_request_id  TEXT,
    prompt_used     TEXT,
    render_params   JSONB,
    error_message   TEXT,
    generation_ms   INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_renders_project_id ON public.renders(project_id);
CREATE INDEX IF NOT EXISTS idx_renders_spec_id    ON public.renders(spec_id);
CREATE INDEX IF NOT EXISTS idx_renders_status     ON public.renders(render_status);

-- ============================================================
-- TECHNICAL FLATS (SVG line drawings)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.technical_flats (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id         UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    view_type       TEXT NOT NULL DEFAULT 'front' CHECK (view_type IN ('front', 'back')),
    svg_content     TEXT,
    storage_path    TEXT,
    public_url      TEXT,
    flat_status     TEXT NOT NULL DEFAULT 'pending' CHECK (flat_status IN ('pending', 'generating', 'complete', 'error')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_technical_flats_project_id ON public.technical_flats(project_id);

-- ============================================================
-- PATTERNS (deterministic geometry engine output)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.patterns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id             UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    piece_name          TEXT NOT NULL,
    svg_content         TEXT,
    dxf_storage_path    TEXT,
    svg_storage_path    TEXT,
    geometry_params     JSONB,
    graded_sizes        JSONB,
    seam_allowance      FLOAT NOT NULL DEFAULT 1.5,
    pattern_status      TEXT NOT NULL DEFAULT 'pending' CHECK (pattern_status IN ('pending', 'generating', 'complete', 'error')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patterns_project_id ON public.patterns(project_id);

-- ============================================================
-- TECH PACKS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.techpacks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id         UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    techpack_json   JSONB,
    pdf_storage_path TEXT,
    pdf_url         TEXT,
    pack_status     TEXT NOT NULL DEFAULT 'pending' CHECK (pack_status IN ('pending', 'generating', 'complete', 'error')),
    ai_provider     TEXT DEFAULT 'gemini-2.5-flash',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_techpacks_project_id ON public.techpacks(project_id);

-- ============================================================
-- MANUFACTURING DOCS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.manufacturing_docs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id         UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    doc_json        JSONB,
    doc_status      TEXT NOT NULL DEFAULT 'pending' CHECK (doc_status IN ('pending', 'generating', 'complete', 'error')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_manufacturing_docs_project_id ON public.manufacturing_docs(project_id);

-- ============================================================
-- TREND REPORTS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.trend_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    spec_id         UUID NOT NULL REFERENCES public.garment_specs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    report_json     JSONB,
    report_status   TEXT NOT NULL DEFAULT 'pending' CHECK (report_status IN ('pending', 'generating', 'complete', 'error')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trend_reports_project_id ON public.trend_reports(project_id);

-- ============================================================
-- EXPORTS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.exports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    export_type     TEXT NOT NULL CHECK (export_type IN ('png', 'svg', 'pdf', 'zip', 'dxf', 'whatsapp')),
    storage_path    TEXT,
    public_url      TEXT,
    expires_at      TIMESTAMPTZ,
    includes        JSONB,
    export_status   TEXT NOT NULL DEFAULT 'pending' CHECK (export_status IN ('pending', 'generating', 'complete', 'error')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exports_project_id ON public.exports(project_id);

-- ============================================================
-- updated_at trigger (applied to profiles, projects, garment_specs, renders)
-- ============================================================
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_garment_specs_updated_at
    BEFORE UPDATE ON public.garment_specs
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_renders_updated_at
    BEFORE UPDATE ON public.renders
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
