"""add counties coords indicators aq stations

Revision ID: a1b2c3d4e5f6
Revises: 264fd480b35a
Create Date: 2026-09-29 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "264fd480b35a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROMANIA_COUNTIES = [
    ("ALBA", "RO121", "RO12", 46.07, 23.58),
    ("ARAD", "RO421", "RO42", 46.19, 21.31),
    ("ARGES", "RO311", "RO31", 45.00, 24.88),
    ("BACAU", "RO211", "RO21", 46.45, 26.88),
    ("BIHOR", "RO111", "RO11", 47.05, 22.10),
    ("BISTRITA-NASAUD", "RO114", "RO11", 47.18, 24.50),
    ("BOTOSANI", "RO212", "RO21", 47.75, 26.67),
    ("BRAILA", "RO221", "RO22", 45.15, 27.75),
    ("BRASOV", "RO122", "RO12", 45.65, 25.40),
    ("BUCURESTI", "RO321", "RO32", 44.43, 26.10),
    ("BUZAU", "RO222", "RO22", 45.15, 26.82),
    ("CALARASI", "RO312", "RO31", 44.30, 27.00),
    ("CARAS-SEVERIN", "RO422", "RO42", 45.20, 22.00),
    ("CLUJ", "RO113", "RO11", 46.77, 23.60),
    ("CONSTANTA", "RO223", "RO22", 44.18, 28.40),
    ("COVASNA", "RO123", "RO12", 45.85, 26.00),
    ("DAMBOVITA", "RO313", "RO31", 44.95, 25.45),
    ("DOLJ", "RO411", "RO41", 44.20, 23.80),
    ("GALATI", "RO224", "RO22", 45.75, 27.95),
    ("GIURGIU", "RO314", "RO31", 44.10, 25.95),
    ("GORJ", "RO412", "RO41", 45.00, 23.30),
    ("HARGHITA", "RO124", "RO12", 46.40, 25.55),
    ("HUNEDOARA", "RO423", "RO42", 45.75, 22.90),
    ("IALOMITA", "RO315", "RO31", 44.60, 27.35),
    ("IASI", "RO213", "RO21", 47.20, 27.40),
    ("ILFOV", "RO322", "RO32", 44.50, 26.10),
    ("MARAMURES", "RO115", "RO11", 47.70, 24.00),
    ("MEHEDINTI", "RO413", "RO41", 44.60, 22.80),
    ("MURES", "RO125", "RO12", 46.55, 24.55),
    ("NEAMT", "RO214", "RO21", 46.95, 26.40),
    ("OLT", "RO414", "RO41", 44.30, 24.50),
    ("PRAHOVA", "RO316", "RO31", 45.10, 26.00),
    ("SALAJ", "RO112", "RO11", 47.20, 23.05),
    ("SATU-MARE", "RO116", "RO11", 47.80, 22.90),
    ("SIBIU", "RO126", "RO12", 45.80, 24.15),
    ("SUCEAVA", "RO215", "RO21", 47.55, 25.80),
    ("TELEORMAN", "RO317", "RO31", 44.00, 25.20),
    ("TIMIS", "RO424", "RO42", 45.75, 21.30),
    ("TULCEA", "RO225", "RO22", 45.00, 28.80),
    ("VALCEA", "RO415", "RO41", 45.10, 24.30),
    ("VASLUI", "RO216", "RO21", 46.55, 27.80),
    ("VRANCEA", "RO226", "RO22", 45.80, 27.00),
]


def upgrade() -> None:
    op.create_table(
        "counties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("nuts3", sa.String(length=10), nullable=False),
        sa.Column("nuts2", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
    )
    op.create_index("ix_counties_name", "counties", ["name"], unique=True)
    op.create_index("ix_counties_nuts3", "counties", ["nuts3"], unique=True)
    op.create_index("ix_counties_nuts2", "counties", ["nuts2"], unique=False)

    counties_table = sa.table(
        "counties",
        sa.column("name", sa.String),
        sa.column("nuts3", sa.String),
        sa.column("nuts2", sa.String),
        sa.column("latitude", sa.Float),
        sa.column("longitude", sa.Float),
    )
    op.bulk_insert(
        counties_table,
        [
            {
                "name": name,
                "nuts3": nuts3,
                "nuts2": nuts2,
                "latitude": lat,
                "longitude": lon,
            }
            for name, nuts3, nuts2, lat, lon in ROMANIA_COUNTIES
        ],
    )

    op.add_column("localities", sa.Column("county_id", sa.Integer(), nullable=True))
    op.add_column("localities", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("localities", sa.Column("longitude", sa.Float(), nullable=True))
    op.create_foreign_key(
        "fk_localities_county_id",
        "localities",
        "counties",
        ["county_id"],
        ["id"],
    )
    op.create_index("ix_localities_county_id", "localities", ["county_id"])

    op.execute(
        """
        UPDATE localities AS l
        SET county_id = c.id
        FROM counties AS c
        WHERE upper(l.county) = c.name
        """
    )

    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("geo_level", sa.String(length=20), nullable=False),
        sa.Column("dataset_code", sa.String(length=80), nullable=True),
        sa.Column("theme", sa.String(length=80), nullable=True),
    )
    op.create_index("ix_indicators_code", "indicators", ["code"], unique=True)
    op.create_index("ix_indicators_source", "indicators", ["source"])
    op.create_index("ix_indicators_geo_level", "indicators", ["geo_level"])

    op.create_table(
        "indicator_values",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("geo_code", sa.String(length=20), nullable=False),
        sa.Column("time_period", sa.String(length=20), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["indicator_id"],
            ["indicators.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "indicator_id",
            "geo_code",
            "time_period",
            name="uq_indicator_geo_time",
        ),
    )
    op.create_index("ix_indicator_values_indicator_id", "indicator_values", ["indicator_id"])
    op.create_index("ix_indicator_values_geo_code", "indicator_values", ["geo_code"])

    op.create_table(
        "aq_stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("eoi_code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("county_id", sa.Integer(), nullable=True),
        sa.Column("nuts3", sa.String(length=10), nullable=True),
        sa.Column("pollutants", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["county_id"], ["counties.id"]),
    )
    op.create_index("ix_aq_stations_eoi_code", "aq_stations", ["eoi_code"], unique=True)
    op.create_index("ix_aq_stations_county_id", "aq_stations", ["county_id"])
    op.create_index("ix_aq_stations_nuts3", "aq_stations", ["nuts3"])


def downgrade() -> None:
    op.drop_table("aq_stations")
    op.drop_table("indicator_values")
    op.drop_table("indicators")
    op.drop_constraint("fk_localities_county_id", "localities", type_="foreignkey")
    op.drop_index("ix_localities_county_id", table_name="localities")
    op.drop_column("localities", "longitude")
    op.drop_column("localities", "latitude")
    op.drop_column("localities", "county_id")
    op.drop_table("counties")
