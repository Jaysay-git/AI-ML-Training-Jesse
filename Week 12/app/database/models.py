from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default="user", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    prices: Mapped[list["Price"]] = relationship(
        back_populates="creator"
    )


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(100), nullable=False)

    prices: Mapped[list["Price"]] = relationship(
        back_populates="commodity"
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("city", "state", name="uq_city_state"),
    )

    prices: Mapped[list["Price"]] = relationship(
        back_populates="location"
    )


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False)
    data_source: Mapped[str] = mapped_column(
        String(50), default="USER_SUBMITTED", nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_price_positive"),
        UniqueConstraint(
            "commodity_id",
            "location_id",
            "recorded_at",
            name="uq_commodity_location_date",
        ),
    )

    commodity: Mapped["Commodity"] = relationship(
        back_populates="prices"
    )
    location: Mapped["Location"] = relationship(
        back_populates="prices"
    )
    creator: Mapped["User | None"] = relationship(
        back_populates="prices"
    )
