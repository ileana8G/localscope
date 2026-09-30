from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base


class County(Base):
    __tablename__ = "counties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    nuts3: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    nuts2: Mapped[str] = mapped_column(String(10), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    localities = relationship("Locality", back_populates="county_rel")
