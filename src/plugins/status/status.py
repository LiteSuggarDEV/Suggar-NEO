from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher

from src.plugins.menu.models import MatcherData
from src.plugins.menu.utils import CSS_PATH, cached_md_to_pic
from suggar_utils.utils import generate_info


@on_command(
    "status",
    aliases={"状态", "info"},
    block=True,
    state=MatcherData(
        rm_name="Suggar状态查询", rm_usage="/info", rm_desc="查询Suggar的运行状态"
    ).model_dump(),
).handle()
async def status(matcher: Matcher):
    md = generate_info()
    pic = await cached_md_to_pic(md, str(CSS_PATH))
    await matcher.finish(MessageSegment.image(pic))
