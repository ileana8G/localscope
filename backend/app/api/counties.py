from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.county import County
from backend.app.schemas.county import CountyResponse
from backend.app.services.dashboard import build_county_dashboard

router = APIRouter(
    prefix="/api/v1/counties",
    tags=["counties"],
)


@router.get("/", response_model=list[CountyResponse])
def list_counties(db: Session = Depends(get_db)):
    statement = select(County).order_by(County.name)
    return db.scalars(statement).all()


@router.get("/search", response_model=list[CountyResponse])
def search_counties(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    statement = (
        select(County)
        .where(County.name.ilike(f"%{q}%"))
        .order_by(County.name)
        .limit(limit)
    )
    return db.scalars(statement).all()


@router.get("/{nuts3}", response_model=CountyResponse)
def get_county(nuts3: str, db: Session = Depends(get_db)):
    county = db.scalar(select(County).where(County.nuts3 == nuts3.upper()))
    if county is None:
        raise HTTPException(status_code=404, detail="County not found")
    return county


@router.get("/{nuts3}/dashboard")
def get_county_dashboard(nuts3: str, db: Session = Depends(get_db)):
    dashboard = build_county_dashboard(db, nuts3)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="County not found")
    return dashboard
