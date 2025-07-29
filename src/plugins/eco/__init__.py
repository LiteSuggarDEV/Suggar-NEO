from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

from suggar_utils.value import SUGGAR_EXP_ID

require("nonebot_plugin_orm")
require("nonebot_plugin_value")
require("nonebot_plugin_suggarchat")
require("menu")

from nonebot_plugin_value.api.api_currency import get_or_create_currency
from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData

from . import auto, query, signin

__plugin_meta__ = PluginMetadata(
    type="application",
    name="经济",
    description="经济功能应用实现插件",
    usage="经济功能",
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
