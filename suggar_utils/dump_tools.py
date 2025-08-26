import json
from asyncio import Lock
from datetime import datetime

from aiofiles import open
from nonebot import logger
from nonebot.plugin import require
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import (
    add_balance,
    del_account,
    get_or_create_account,
    list_accounts,
)
from pydantic import BaseModel, Field

require("amrita.plugins.manager")
from amrita.plugins.manager.status_manager import StatusManager

from .store import DUMP_PATH, UPDATE_FILE, UserModel, get_or_create_user_model
from .value import SUGGAR_EXP_ID, to_uuid

db_lock = Lock()


class UserFunDataSchema(BaseModel):
    """
    用户功能数据模型
    """

    id: str = Field(default_factory=str)  # 用户ID
    sign_day: int = Field(default_factory=int)  # 签到天数
    timestamp: float = Field(default_factory=float)  # 最后一次签到时间戳
    coin: float = Field(default_factory=float)  # 金币
    exp: float = Field(default_factory=float)  # 经验


async def reset_by_data(
    data: UserFunDataSchema,
) -> None:
    """通过UserFunDataSchema重置用户数据

    Args:
        data (UserFunDataSchema): 数据模型
    """
    logger.warning(f"正在重写用户数据{data.id}")
    await del_account(data.id)
    await del_account(data.id, SUGGAR_EXP_ID)
    await add_balance(data.id, data.coin if data.coin > 0 else 10, "system")
    await add_balance(
        data.id, data.exp if data.exp > 0 else 1, "system", currency_id=SUGGAR_EXP_ID
    )
    async with get_session() as session:
        user_model: UserModel = await get_or_create_user_model(data.id, session)
        session.add(user_model)
        user_model.daily_count = data.sign_day
        user_model.last_daily = datetime.fromtimestamp(data.timestamp)
        await session.commit()


async def reset_all_by_data(data: list[UserFunDataSchema]) -> None:
    """通过data列表重置所有用户数据

    Args:
        data (list[UserFunDataSchema]): 数据
    """

    for d in data:
        await reset_by_data(d)


async def reset_from_update_file():
    async with db_lock:
        try:
            StatusManager().set_unready(True)
            if not UPDATE_FILE.exists():
                logger.warning(f"JSON文件({UPDATE_FILE!s})不存在")
                return
            async with open(UPDATE_FILE, encoding="utf-8") as f:
                f_str = await f.read()
            data_list: list[dict] = json.loads(f_str)
            final_list: list[UserFunDataSchema] = [
                UserFunDataSchema(**d) for d in data_list
            ]
            for d in final_list:
                if type(d.id) is int:
                    d.id = to_uuid(str(d.id))
            await reset_all_by_data(final_list)
        finally:
            StatusManager().set_unready(False)


async def dump_to_json():
    async with db_lock:
        try:
            StatusManager().set_unready(True)
            eco_accounts = await list_accounts()
            final_list = []
            for acc in eco_accounts:
                uid = acc.id
                eco_value = acc.balance
                exp_data = await get_or_create_account(uid, SUGGAR_EXP_ID)
                exp_value = exp_data.balance
                async with get_session() as session:
                    fun_data = await get_or_create_user_model(uid, session)
                    final_list.append(
                        dict(
                            UserFunDataSchema(
                                id=uid,
                                coin=eco_value,
                                exp=exp_value,
                                sign_day=fun_data.daily_count,
                                timestamp=fun_data.last_daily.timestamp(),
                            )
                        )
                    )
            async with open(DUMP_PATH, "w", encoding="utf-8") as f:
                await f.write(json.dumps(final_list, ensure_ascii=False, indent=4))
        finally:
            StatusManager().set_unready(False)
