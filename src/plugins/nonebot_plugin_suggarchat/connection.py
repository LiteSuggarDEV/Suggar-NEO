from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot

from .config import config_manager
from .hook_manager import run_hooks

driver = get_driver()


@driver.on_bot_connect
async def onConnect(bot: Bot):
    await run_hooks(bot)


@driver.on_startup
async def onEnable():
    logger.info("正在加载SuggarChat，加载配置文件与数据中......")
    config_manager.load()
    logger.info("启动完成。")
