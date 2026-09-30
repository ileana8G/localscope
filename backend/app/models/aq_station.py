from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class AqStation(Base):
    __tablename__ = "aq_stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    eoi_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    county_id: Mapped[int | None] = mapped_column(
        ForeignKey("counties.id"),
        nullable=True,
        index=True,
    )
    nuts3: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    pollutants: Mapped[str | None] = mapped_column(String(255), nullable=True)
