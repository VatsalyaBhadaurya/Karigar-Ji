-- KarigarJi Row Level Security Policies
-- Apply AFTER schema.sql

-- Enable RLS on all tables
ALTER TABLE public.profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.garment_specs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.renders           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technical_flats   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patterns          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.techpacks         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manufacturing_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_reports     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports           ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- PROFILES: users can only read/update their own profile
-- ============================================================
CREATE POLICY "profiles_select_own"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "profiles_update_own"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- ============================================================
-- PROJECTS: full ownership
-- ============================================================
CREATE POLICY "projects_all_own"
    ON public.projects FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- UPLOADS
-- ============================================================
CREATE POLICY "uploads_all_own"
    ON public.uploads FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- GARMENT SPECS
-- ============================================================
CREATE POLICY "garment_specs_all_own"
    ON public.garment_specs FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- RENDERS
-- ============================================================
CREATE POLICY "renders_all_own"
    ON public.renders FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- TECHNICAL FLATS
-- ============================================================
CREATE POLICY "technical_flats_all_own"
    ON public.technical_flats FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- PATTERNS
-- ============================================================
CREATE POLICY "patterns_all_own"
    ON public.patterns FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- TECH PACKS
-- ============================================================
CREATE POLICY "techpacks_all_own"
    ON public.techpacks FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- MANUFACTURING DOCS
-- ============================================================
CREATE POLICY "manufacturing_docs_all_own"
    ON public.manufacturing_docs FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- TREND REPORTS
-- ============================================================
CREATE POLICY "trend_reports_all_own"
    ON public.trend_reports FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- EXPORTS
-- ============================================================
CREATE POLICY "exports_all_own"
    ON public.exports FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- NOTE: Backend FastAPI uses service_role key → bypasses RLS
-- Frontend uses anon key → all RLS policies apply
