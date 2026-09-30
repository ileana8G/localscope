from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    geo_level: Mapped[str] = mapped_column(String(20), index=True)
    dataset_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    theme: Mapped[str | None] = mapped_column(String(80), nullable=True)


class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    __table_args__ = (
        UniqueConstraint(
            "indicator_id",
            "geo_code",
            "time_period",
            name="uq_indicator_geo_time",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[int] = mapped_column(
        ForeignKey("indicators.id", ondelete="CASCADE"),
        index=True,
    )
    geo_code: Mapped[str] = mapped_column(String(20), index=True)
    time_period: Mapped[str] = mapped_column(String(20))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
