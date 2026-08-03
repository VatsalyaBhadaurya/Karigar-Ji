from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.dependencies import CurrentUser, get_db
from app.exceptions import NotFoundError

router = APIRouter(prefix="/pattern", tags=["pattern"])


class PatternRequest(BaseModel):
    spec_id: str
    project_id: str
    sizes: list[str] = ["S", "M", "L"]


@router.post("")
async def generate_pattern(
    body: PatternRequest,
    current_user: CurrentUser = None,
    db: Client = Depends(get_db),
):
    """
    Pattern generation via deterministic geometry engine.
    Phase 5 implementation — geometry modules live in ai/pattern_engine/.
    """
    user_id: str = current_user["sub"]

    spec_row = (
        db.table("garment_specs")
        .select("spec_json")
        .eq("id", body.spec_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not spec_row.data:
        raise NotFoundError("GarmentSpec", body.spec_id)

    # Phase 5: will call pattern_engine blocks here
    return {
        "message": "Pattern engine — Phase 5 (coming soon)",
        "spec_id": body.spec_id,
        "sizes_requested": body.sizes,
    }
