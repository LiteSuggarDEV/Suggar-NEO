from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
require("nonebot_plugin_value")

from nonebot_plugin_orm import get_session
from nonebot_plugin_value import get_or_create_currency
from nonebot_plugin_value.api.api_balance import (
    batch_add_balance,
    del_account,
    list_accounts,
)

from suggar_utils.config import config_manager

from . import command, functions
from .functions import update_fish, update_quilty
from .pyd_models import DEFAULT_FISH_LIST, DEFAULT_QUALITY, FISHING_POINT

driver = get_driver()

__plugin_meta__ = PluginMetadata(
    name="赛博钓鱼",
    description="一个简单的钓鱼插件，来当赛博钓鱼佬罢！",
    usage="",
    type="application",
)

__all__ = [
    "command",
    "functions",
]


@driver.on_startup
async def init_fish():
    async with get_session() as session:
        logger.info("正在初始化鱼")
        for quality in DEFAULT_QUALITY:
            await update_quilty(quality, session)
        for fish in DEFAULT_FISH_LIST:
            await update_fish(fish, session)
    await get_or_create_currency(FISHING_POINT)
    if config_manager.config.fishing.eco2fishing:
        logger.warning("正在将账户余额转换为钓鱼积分...")
        accounts = await list_accounts()
        account_balance: list[tuple[str, float]] = [
            (account.id, account.balance) for account in accounts
        ]

        await batch_add_balance(account_balance, currency_id=FISHING_POINT.id)
        for account in accounts:
            await del_account(account.id)
        config_manager.config.fishing.eco2fishing = False
        await config_manager.save_config()
        await config_manager.reload_config()
        logger.info("账户余额转换为钓鱼积分完成")
    logger.info("赛博钓鱼初始化完成")
