from __future__ import annotations

import logging
import mimetypes
import uuid
from pathlib import Path

from supabase import Client

from app.config import settings
from app.exceptions import StorageError

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class StorageService:
    def __init__(self, db: Client) -> None:
        self._db = db
        self._bucket = settings.SUPABASE_STORAGE_BUCKET

    def upload_sketch(
        self,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
        user_id: str,
        project_id: str,
    ) -> tuple[str, str]:
        """
        Upload a sketch file to Supabase Storage.
        Returns (storage_path, public_url).
        """
        if mime_type not in ALLOWED_MIME_TYPES:
            raise StorageError(f"Unsupported file type: {mime_type}. Allowed: JPEG, PNG, WEBP, PDF")
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise StorageError("File exceeds 20 MB limit")

        ext = Path(file_name).suffix or mimetypes.guess_extension(mime_type) or ""
        safe_name = f"{uuid.uuid4()}{ext}"
        storage_path = f"{user_id}/{project_id}/uploads/v1/{safe_name}"

        try:
            self._db.storage.from_(self._bucket).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": mime_type},
            )
            public_url = self._db.storage.from_(self._bucket).get_public_url(storage_path)
            return storage_path, public_url
        except Exception as exc:
            logger.exception("Storage upload failed")
            raise StorageError(str(exc)) from exc

    def upload_artifact(
        self,
        file_bytes: bytes,
        artifact_type: str,
        file_name: str,
        mime_type: str,
        user_id: str,
        project_id: str,
        version: int = 1,
    ) -> tuple[str, str]:
        """Upload any generated artifact. Returns (storage_path, public_url)."""
        storage_path = f"{user_id}/{project_id}/{artifact_type}/v{version}/{file_name}"
        try:
            self._db.storage.from_(self._bucket).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": mime_type},
            )
            public_url = self._db.storage.from_(self._bucket).get_public_url(storage_path)
            return storage_path, public_url
        except Exception as exc:
            logger.exception("Artifact upload failed: %s", artifact_type)
            raise StorageError(str(exc)) from exc

    def create_signed_url(self, storage_path: str, expires_in: int = 86400) -> str:
        """Create a signed URL valid for expires_in seconds (default 24h)."""
        try:
            result = self._db.storage.from_(self._bucket).create_signed_url(
                storage_path, expires_in
            )
            return result["signedURL"]
        except Exception as exc:
            raise StorageError(str(exc)) from exc
