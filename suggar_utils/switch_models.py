from collections.abc import Awaitable, Callable
from enum import Enum

from nonebot import require
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from sqlalchemy import String, insert, select
from sqlalchemy.orm import MappedColumn, mapped_column

require("nonebot_plugin_orm")
from nonebot_plugin_orm import AsyncSession, Model, get_session

from .store import to_uuid


class FuncEnum(str, Enum):
    FISHING = "fishing_enabled"
    DAILY = "daily_enabled"
    LUCK = "luck_enabled"


class FunctionSwitch(Model):
    __tablename__ = "suggar_function_switch"
    group_id: MappedColumn[str] = mapped_column(String(255), primary_key=True)
    fishing_enabled: MappedColumn[bool] = mapped_column(default=True)
    daily_enabled: MappedColumn[bool] = mapped_column(default=True)
    luck_enabled: MappedColumn[bool] = mapped_column(default=True)


async def get_or_create_switch(group_id: str, session: AsyncSession) -> FunctionSwitch:
    async with session:
        stmt = (
            select(FunctionSwitch)
            .where(FunctionSwitch.group_id == group_id)
            .with_for_update()
        )
        result = await session.execute(stmt)
        switch = result.scalar_one_or_none()
        if not switch:
            stmt = insert(FunctionSwitch).values(group_id=group_id)
            await session.execute(stmt)
            await session.commit()
            switch = (
                await session.execute(
                    select(FunctionSwitch).where(FunctionSwitch.group_id == group_id)
                )
            ).scalar_one()
        session.add(switch)
        return switch


def is_enabled(func_name: FuncEnum) -> Callable[..., Awaitable[bool]]:
    """
    判断当前群组是否启用功能
    """

    async def check(event: GroupMessageEvent) -> bool:
        group_id = to_uuid(str(event.group_id))
        async with get_session() as session:
            data = await get_or_create_switch(group_id, session)
            return getattr(data, func_name.value)

    return check
