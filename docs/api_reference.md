# KarigarJi API Reference

Base URL: `http://localhost:8000/api/v1` (dev) | `https://api.karigarji.com/api/v1` (prod)

All endpoints require `Authorization: Bearer <supabase_jwt>` header.

## Upload

### `POST /upload`
Upload a sketch image.

**Request**: `multipart/form-data`
- `file`: JPEG / PNG / WEBP / PDF (max 20MB)
- `project_id`: UUID

**Response**:
```json
{ "upload_id": "uuid", "storage_path": "...", "public_url": "..." }
```

---

## Vision

### `POST /vision/analyze`
Analyze uploaded sketch → GarmentSpec JSON.

**Request**:
```json
{ "upload_id": "uuid", "project_id": "uuid", "user_notes": "optional" }
```

**Response**: Full `GarmentSpec` object + `spec_id`

### `GET /vision/spec/{spec_id}`
Retrieve a specific garment spec.

### `PATCH /vision/spec/{spec_id}`
Update spec fields (manual editing after AI generation).

---

## Render

### `POST /render`
Trigger photorealistic render generation.

**Request**:
```json
{ "spec_id": "uuid", "project_id": "uuid", "views": ["front","back","side","studio"] }
```

**Response**: Array of render job objects with `render_id` and initial `status: "queued"`

### `GET /render/{render_id}`
Poll render status. When `status: "complete"`, `public_url` is populated.

---

## Tech Pack

### `POST /techpack`
Generate tech pack from garment spec.

**Request**: `{ "spec_id": "uuid", "project_id": "uuid" }`

**Response**: `{ "techpack_id": "uuid", "status": "pending" }`

---

## Pattern

### `POST /pattern`
Generate pattern pieces (deterministic geometry).

**Request**: `{ "spec_id": "uuid", "project_id": "uuid", "sizes": ["S","M","L"] }`

---

## Manufacturing

### `POST /manufacturing`
Generate manufacturing documentation.

**Request**: `{ "spec_id": "uuid", "project_id": "uuid" }`

---

## Trend

### `POST /trend`
Generate trend analysis report.

**Request**: `{ "spec_id": "uuid", "project_id": "uuid" }`

---

## Export

### `POST /export`
Bundle artifacts for download.

**Request**:
```json
{
  "project_id": "uuid",
  "export_type": "zip",
  "include": ["renders", "techpack", "patterns", "flats"]
}
```

**Response**: `{ "export_id": "uuid", "download_url": "...", "expires_at": "..." }`

---

## Project

### `GET /project/{id}`
Full project with all artifact statuses.

### `PATCH /project/{id}`
Update project name, description, status.
