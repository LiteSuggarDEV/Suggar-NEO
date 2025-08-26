from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
require("nonebot_plugin_value")
require("amrita.plugins.chat")
require("menu")
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import list_accounts
from nonebot_plugin_value.api.api_currency import (
    get_or_create_currency,
)
from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData
from nonebot_plugin_value.repository import AccountRepository

from suggar_utils.config import config_manager
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
    if config_manager.config.reset_balance:
        logger.warning("正在重置所有用户的余额...")
        accounts = await list_accounts()
        async with get_session() as session:
            repo = AccountRepository(session)
            for account in accounts:
                if account.balance > 8000000:
                    await repo.update_balance(
                        account.id, account.balance / 1000, account.currency_id
                    )
        config_manager.config.reset_balance = False
        await config_manager.save_config()
        await config_manager.reload_config()
    logger.info("货币初始化完成")
