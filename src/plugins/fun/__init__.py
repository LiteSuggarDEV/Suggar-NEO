from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
require("nonebot_plugin_value")
require("nonebot_plugin_suggarchat")
require("menu")
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import list_accounts
from nonebot_plugin_value.api.api_currency import (
    get_default_currency,
    get_or_create_currency,
)
from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData
from nonebot_plugin_value.repository import AccountRepository

from suggar_utils.value import SUGGAR_EXP_ID

from . import auto, query, signin

__plugin_meta__ = PluginMetadata(
    type="application",
    name="娱乐插件",
    description="娱乐功能应用实现插件",
    usage="娱乐功能",
)
__all__ = [
    "auto",
    "query",
    "signin",
]


@get_driver().on_startup
async def init_currency():
    logger.info("初始化货币...")
    await get_or_create_currency(
        CurrencyData(
            id=SUGGAR_EXP_ID,
            allow_negative=True,
            display_name="exp",
            symbol="EXP",
        )
    )
    accounts = await list_accounts()
    async with get_session() as session:
        repo = AccountRepository(session)
        currency_id = (await get_default_currency()).id
        for account in accounts:
            if account.balance >= 20000000:
                await repo.update_balance(account.id, 20000000, currency_id)
