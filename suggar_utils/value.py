from nonebot import require

require("nonebot_plugin_value")
from nonebot_plugin_value.api.api_balance import (
    UserAccountData,
    get_or_create_account,
)
from nonebot_plugin_value.api.api_balance import (
    add_balance as add_b,
)
from nonebot_plugin_value.api.api_balance import (
    del_balance as del_b,
)
from nonebot_plugin_value.uuid_lib import to_uuid

SUGGAR_VALUE_ID = to_uuid("love")
SUGGAR_EXP_ID = to_uuid("exp")


async def add_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> UserAccountData:
    user_id = to_uuid(user_id)
    await get_or_create_account(user_id, currency_id)
    return await add_b(user_id, amount, source, currency_id)


async def del_balance(
    user_id: str,
    amount: float,
    source: str = "_transfer",
    currency_id: str | None = None,
) -> UserAccountData:
    user_id = to_uuid(user_id)
    await get_or_create_account(user_id, currency_id)
    return await del_b(user_id, amount, source, currency_id)
