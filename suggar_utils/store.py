from datetime import datetime

from nonebot import require
from nonebot_plugin_orm import AsyncSession, Model
from sqlalchemy import DateTime, Integer, String, insert, select
from sqlalchemy.orm import MappedColumn, load_only, mapped_column

require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_config_dir, get_data_dir

DATA_DIR = get_data_dir("suggar_original")
CONFIG_DIR = get_config_dir("suggar_original")


class UserModel(Model):
    __tablename__ = "suggar_user_data"

    user_id: MappedColumn[str] = mapped_column(String(50), primary_key=True)
    last_daily: MappedColumn[datetime] = mapped_column(
        DateTime, default=datetime.fromtimestamp(0.0), nullable=False
    )
    daily_count: MappedColumn[int] = mapped_column(Integer, default=0, nullable=False)


async def get_user_or_none(user_id: str, session: AsyncSession) -> UserModel | None:
    async with session:
        stmt = (
            select(UserModel)
            .where(UserModel.user_id == user_id)
            .options(load_only(UserModel.last_daily, UserModel.daily_count))
            .with_for_update()
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user


async def get_or_create_user_model(user_id: str, session: AsyncSession) -> UserModel:
    async with session:
        if (data := await get_user_or_none(user_id, session)) is not None:
            return data
        else:
            stmt = insert(UserModel).values(user_id=user_id)
            await session.execute(stmt)
            user = await get_user_or_none(user_id, session)
            assert user is not None, "ERROR:UserModel is None!"
            return user
