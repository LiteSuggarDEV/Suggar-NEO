from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_orm")
require("nonebot_plugin_value")

from nonebot_plugin_orm import get_session

from . import command, functions
from .functions import update_fish, update_quilty
from .pyd_models import DEFAULT_FISH_LIST, DEFAULT_QUALITY

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
