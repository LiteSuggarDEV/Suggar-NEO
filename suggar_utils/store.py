from datetime import datetime

from nonebot import require
from nonebot_plugin_orm import AsyncSession, Model
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import MappedColumn, mapped_column

require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_config_dir, get_data_dir

DATA_DIR = get_data_dir("suggar_original")
CONFIG_DIR = get_config_dir("suggar_original")


class UserModel(Model):
    __tablename__ = "suggar_user_data"

    user_id: MappedColumn[str] = mapped_column(String(50), primary_key=True)
    last_daily: MappedColumn[datetime] = mapped_column(
        DateTime, default=0.0, nullable=False
    )
    daily_count: MappedColumn[int] = mapped_column(Integer, default=0, nullable=False)


async def get_or_create_user_model(user_id: str, session: AsyncSession) -> UserModel:
    async with session:
        stmt = select(UserModel).where(UserModel.user_id == user_id).with_for_update()
        result = await session.execute(stmt)
        if (data := result.scalar_one_or_none()) is not None:
            return data
        else:
            user = UserModel(
                user_id=user_id, last_daily=datetime.fromtimestamp(0.0), daily_count=0
            )

            session.add(user)
            await session.commit()
            return user
