from nonebot import on_command
from nonebot.matcher import Matcher

from src.plugins.menu.models import MatcherData
from suggar_utils.dump_tools import reset_from_update_file
from suggar_utils.rule import is_global_admin


@on_command(
    "reset_data",
    state=dict(
        MatcherData(rm_name="重置数据", rm_desc="重置数据", rm_usage="/reset_data")
    ),
    permission=is_global_admin,
).handle()
async def _(matcher: Matcher) -> None:
    await reset_from_update_file()
    await matcher.finish("数据已重置")
