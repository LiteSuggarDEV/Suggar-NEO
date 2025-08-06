from datetime import datetime

from nonebot import require
from sqlalchemy import (
    FLOAT,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

require("nonebot_plugin_orm")
from nonebot_plugin_orm import Model


class UserFishMetaData(Model):
    __tablename__ = "fishing_user_meta"
    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    lucky_of_the_sea: Mapped[int] = mapped_column(Integer, default=0)
    multi_fish: Mapped[int] = mapped_column(Integer, default=0)
    feeding: Mapped[int] = mapped_column(Integer, default=0)
    last_fishing_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    today_fishing_count: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[str] = mapped_column(
        String(1024),
        default="{}",
        nullable=False,
    )


class QualityMetaData(Model):
    __tablename__ = "fishing_quality_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    probability: Mapped[float] = mapped_column(FLOAT, nullable=False)
    price_per_length: Mapped[float] = mapped_column(FLOAT, nullable=False)
    length_range_start: Mapped[int] = mapped_column(FLOAT, nullable=False)
    length_range_end: Mapped[int] = mapped_column(FLOAT, nullable=False)

    __table_args__ = (UniqueConstraint("name", name="unique_quality_name"),)


class FishMeta(Model):
    __tablename__ = "fish_meta"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    quality: Mapped[str] = mapped_column(
        ForeignKey("fishing_quality_meta.name"), nullable=False
    )
    prompt: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    __table_args__ = (
        Index("idx_fish_meta_name", "name"),
        Index("idx_fish_meta_quality", "quality"),
        UniqueConstraint("name", name="uq_fish_meta_quality_name"),
    )


class FishRecord(Model):
    __tablename__ = "fish_record"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("fishing_user_meta.user_id"), nullable=False
    )
    fish_name: Mapped[str] = mapped_column(ForeignKey("fish_meta.name"), nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_fish_user_id", "user_id"),
        Index("idx_fish_fish_name", "fish_name"),
    )
