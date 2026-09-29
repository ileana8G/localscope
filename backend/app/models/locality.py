from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class Locality(Base):
    __tablename__ = "localities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    county: Mapped[str] = mapped_column(String(100))