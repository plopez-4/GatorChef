from fastapi import APIRouter, Depends, Query

from app.deps import verify_firebase_token
from app.models import RecipeMatch

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/match", response_model=list[RecipeMatch])
async def match_recipes(
    top: int = Query(default=5, ge=1, le=20),
    token: dict = Depends(verify_firebase_token),
):
    # TODO Phase 4: implement recipe matching
    # 1. Fetch user's pantry items
    # 2. Call recipe_service.match_recipes(pantry_items, top)
    # 3. Return list of RecipeMatch
    raise NotImplementedError
