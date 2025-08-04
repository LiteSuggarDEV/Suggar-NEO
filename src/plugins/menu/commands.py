import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
)

from suggar_utils.config import config_manager
from suggar_utils.utils import send_forward_msg

from .models import CategoryEnum, CommandParam, MatcherData, ParamType
from .utils import (
    cached_html_to_pic,
    get_page_html,
)

command_start = get_driver().config.command_start


@nonebot.on_command(
    (f"{prefix}menu" for prefix in command_start),
    state=MatcherData(
        name="Menu",
        description="展示菜单",
        usage="/menu",
        params=[
            CommandParam(
                name="板块",
                description="菜单板块",
                param_type=ParamType.OPTIONAL,
            )
        ],
        category=CategoryEnum.UTILS,
    ).model_dump(),
    priority=10,
    block=True,
).handle()
async def show_menu(bot: Bot, event: MessageEvent):
    """显示菜单"""
    if not config_manager.config.enable_menu:
        return

    menus = [await cached_html_to_pic(page) for page in get_page_html()]

    markdown_menus_pics = [
        *(MessageSegment.image(file=menu) for menu in menus),
        MessageSegment.text(
            "Bot开源地址：https://github.com/LiteSuggarDEV/Suggar-NEO/"
        ),
    ]

    await send_forward_msg(
        bot,
        event,
        name="菜单",
        uin=str(bot.self_id),
        msgs=markdown_menus_pics,
    )
