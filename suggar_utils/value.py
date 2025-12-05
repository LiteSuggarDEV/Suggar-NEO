import asyncio
from collections import defaultdict

from nonebot import require

require("nonebot_plugin_value")

from nonebot_plugin_value.api.api_balance import (
    add_balance as add_b,
)
from nonebot_plugin_value.api.api_balance import (
    del_balance as del_b,
)
from nonebot_plugin_value.uuid_lib import to_uuid

SUGGAR_EXP_ID = to_uuid("exp")
VALUE_LOCK = defaultdict(asyncio.Lock)


async def add_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
):
    async with VALUE_LOCK[user_id]:
        user_id = to_uuid(user_id)
        return await add_b(user_id, amount, source, currency_id)


async def del_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
):
    async with VALUE_LOCK[user_id]:
        user_id = to_uuid(user_id)
        return await del_b(user_id, amount, source, currency_id)
