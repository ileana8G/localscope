from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.locality import Locality
from backend.app.schemas.locality import LocalityResponse

router = APIRouter(
    prefix="/api/v1/localities",
    tags=["localities"],
)


@router.get("/", response_model=list[LocalityResponse])
def get_localities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = (
        select(Locality)
        .order_by(Locality.siruta)
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()



@router.get("/search", response_model=list[LocalityResponse])
def search_localities(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    statement = (
        select(Locality)
        .where(Locality.name.ilike(f"%{q}%"))
        .order_by(Locality.name)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{siruta}", response_model=LocalityResponse)
def get_locality(
    siruta: int,
    db: Session = Depends(get_db),
):
    statement = select(Locality).where(Locality.siruta == siruta)
    locality = db.scalar(statement)

    if locality is None:

        raise HTTPException(
            status_code=404,
            detail="Locality not found",
        )

    return locality

