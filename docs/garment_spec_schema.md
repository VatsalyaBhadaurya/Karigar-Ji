# Garment Specification Schema

The `GarmentSpec` is the single source of truth for every project.
It is defined as a Pydantic v2 model in `backend/app/schemas/garment_spec.py`
and mirrored as a TypeScript interface in `frontend/src/lib/types/garment.ts`.

## Top-Level Fields

| Field | Type | Description |
|---|---|---|
| `garment_type` | string | e.g. "kurta", "dress", "blazer", "saree_blouse" |
| `silhouette` | string | e.g. "A-line", "straight", "flared", "fitted" |
| `neckline` | string? | e.g. "round", "V-neck", "mandarin", "sweetheart" |
| `sleeve_type` | string? | e.g. "set-in", "raglan", "sleeveless", "flutter" |
| `fit` | string | e.g. "relaxed", "fitted", "oversized", "slim" |
| `panels` | string[] | Named panels: ["bodice_front", "bodice_back", "yoke"] |
| `pockets` | object[] | Each: `{ type, placement, dimensions }` |
| `collar` | CollarSpec? | `{ type, height, notes }` |
| `cuff` | object? | `{ type, width, closure }` |
| `closure` | object? | `{ type, placement, hardware }` |
| `trims` | string[] | e.g. ["piping", "lace", "buttons"] |
| `embroidery` | EmbroiderySpec? | `{ present, technique, placement, thread_colors }` |
| `construction_notes` | string[] | Free-form construction details |
| `suggested_fabric` | string[] | e.g. ["cotton lawn", "silk crepe"] |
| `colors` | string[] | e.g. ["ivory", "#F5F0E8"] |
| `measurements` | Measurements? | All in cm unless unit specified |
| `seam_allowance` | string | Default "1.5cm" |
| `metadata` | object | `{ confidence, prompt_version, source_type }` |

## Measurements Sub-Schema

```json
{
  "chest": 90.0,
  "waist": 72.0,
  "hip": 96.0,
  "length": 110.0,
  "sleeve_length": 58.0,
  "shoulder_width": 38.0,
  "unit": "cm"
}
```

## Example Full Spec

```json
{
  "garment_type": "anarkali_kurta",
  "silhouette": "flared",
  "neckline": "V-neck",
  "sleeve_type": "set-in",
  "fit": "fitted_bodice_flared_skirt",
  "panels": ["bodice_front", "bodice_back", "skirt_panels_x6", "sleeve_x2"],
  "pockets": [{"type": "side_seam", "placement": "hip", "dimensions": {"width": 15, "depth": 18}}],
  "collar": null,
  "cuff": {"type": "band", "width": 3, "closure": "button"},
  "closure": {"type": "invisible_zipper", "placement": "center_back", "length": 55},
  "trims": ["embroidered_border", "tassel_hem"],
  "embroidery": {
    "present": true,
    "technique": "zardozi",
    "placement": ["neckline", "hem_border", "sleeve_cuff"],
    "thread_colors": ["gold", "ivory"]
  },
  "construction_notes": [
    "French seams on all curved seams",
    "Underlining required for bodice panels"
  ],
  "suggested_fabric": ["georgette", "chiffon"],
  "colors": ["deep_teal", "gold"],
  "measurements": {
    "chest": 90, "waist": 72, "hip": 96,
    "length": 140, "sleeve_length": 58,
    "shoulder_width": 38, "unit": "cm"
  },
  "seam_allowance": "1.5cm",
  "metadata": {
    "confidence": 0.92,
    "prompt_version": "v1.0.0",
    "source_type": "hand_drawn"
  }
}
```
