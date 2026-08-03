# KarigarJi — Architecture Overview

## Core Invariant

Every downstream module consumes the **Garment Spec JSON**, never a raw image.

```
Sketch Image
    ↓
Gemini 2.5 Flash (Vision)
    ↓
GarmentSpec JSON  ← Single Source of Truth
    ↓
┌─────────────────────────────────────────┐
│  Photorealistic Render (FLUX Kontext)   │
│  Technical Flat (SVG renderer)          │
│  Pattern Engine (deterministic geometry)│
│  Tech Pack (Gemini)                     │
│  Manufacturing Doc (Gemini)             │
│  Trend Report (Gemini + Search)         │
│  Fabric Estimator (math only)           │
└─────────────────────────────────────────┘
    ↓
Export (PDF, SVG, DXF, ZIP)
    ↓
WhatsApp Share
```

## Module Boundaries

| Module | Technology | AI Allowed? |
|---|---|---|
| Vision | Gemini 2.5 Flash | Yes — structured JSON only |
| Rendering | FLUX Kontext (fal.ai) | Yes — image generation |
| Technical Flat | SVG rule-based renderer | No — deterministic |
| Pattern Engine | Python geometry | No — math only |
| Tech Pack | Gemini | Yes — structured JSON only |
| Manufacturing | Gemini | Yes — structured JSON only |
| Trend | Gemini + Search Grounding | Yes — structured JSON only |
| Fabric Estimator | Python math | No |
| Export | reportlab, svgwrite, ezdxf | No |

## AI Abstraction Rule

No code outside `backend/app/ai/providers/` may import an AI SDK directly.
All services depend only on the abstract interfaces in `backend/app/ai/base.py`.

## Data Flow

1. User uploads sketch → `StorageService` saves to Supabase Storage → `uploads` row created
2. `VisionService` calls `GeminiProvider.analyze_garment(image_url)` → validated `GarmentSpec`
3. `GarmentSpec` saved to `garment_specs` table (versioned, `is_current=True`)
4. All downstream services receive only `spec_id` → load spec from DB themselves
5. Every artifact stored in Supabase Storage under `{user_id}/{project_id}/{type}/v{n}/`
