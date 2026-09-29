from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/localities", tags=["localities"])


@router.get("/")
def get_localities():
    return [
        {"id": 1, "name": "Ploiești", "county": "Prahova"},
        {"id": 2, "name": "București", "county": "București"},
    ]