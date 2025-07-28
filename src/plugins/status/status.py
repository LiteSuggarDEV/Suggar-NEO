from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher

from src.plugins.menu.models import CategoryEnum, MatcherData
from src.plugins.menu.utils import cached_md_to_pic, get_css_path
from suggar_utils.utils import generate_info


@on_command(
    "status",
    aliases={"状态", "info"},
    block=True,
    state=MatcherData(
        name="Suggar状态查询",
        usage="/info",
        description="查询Suggar的运行状态",
        category=CategoryEnum.UTILS,
    ).model_dump(),
).handle()
async def status(matcher: Matcher):
    md = generate_info()
    pic = await cached_md_to_pic(md, str(get_css_path()))
    await matcher.finish(MessageSegment.image(pic))
