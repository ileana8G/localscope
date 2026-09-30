from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base


class Locality(Base):
    __tablename__ = "localities"

    id: Mapped[int] = mapped_column(primary_key=True)
    siruta: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    county: Mapped[str] = mapped_column(String(100))
    county_id: Mapped[int | None] = mapped_column(
        ForeignKey("counties.id"),
        nullable=True,
        index=True,
    )
    siruta_sup: Mapped[int | None] = mapped_column(Integer, nullable=True)
    locality_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    county_rel = relationship("County", back_populates="localities")
