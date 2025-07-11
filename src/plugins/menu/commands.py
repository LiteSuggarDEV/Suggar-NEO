import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
)
from nonebot.matcher import Matcher

from suggar_utils.utils import send_forward_msg

from .manager import menu_mamager
from .models import MatcherData
from .utils import (
    CSS_PATH,
    cached_md_to_pic,
    generate_markdown_menus,
)

command_start = get_driver().config.command_start


@nonebot.on_fullmatch(
    tuple(
        [f"{prefix}menu" for prefix in command_start]
        + [f"{prefix}菜单" for prefix in command_start]
        + [f"{prefix}help" for prefix in command_start]
    ),
    state=MatcherData(
        rm_name="Menu",
        rm_desc="展示菜单",
        rm_usage="menu",
    ).model_dump(),
).handle()
async def show_menu(matcher: Matcher, bot: Bot, event: MessageEvent):
    """显示菜单"""
    if not menu_mamager.plugins:
        await matcher.finish("菜单加载失败，请检查日志")

    markdown_menus = generate_markdown_menus(menu_mamager.plugins)

    if not markdown_menus:
        await matcher.finish("没有可用的菜单")

    markdown_menus_pics = [
        MessageSegment.image(
            file=await cached_md_to_pic(md=markdown_menus_string, css_path=CSS_PATH)
        )
        for markdown_menus_string in markdown_menus
    ] + [
        MessageSegment.text(
            "Suggar开源地址：https://github.com/LiteSuggarDEV/Suggar-NEO/"
        )
    ]

    await send_forward_msg(
        bot,
        event,
        name="Suggar 菜单",
        uin=str(bot.self_id),
        msgs=markdown_menus_pics,
    )
