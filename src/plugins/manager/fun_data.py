from nonebot import on_command
from nonebot.matcher import Matcher

from src.plugins.menu.models import MatcherData
from suggar_utils.dump_tools import dump_to_json, reset_from_update_file
from suggar_utils.rule import is_global_admin


@on_command(
    "reset_data",
    state=dict(
        MatcherData(
            rm_name="重写数据", rm_desc="从恢复文件重置数据", rm_usage="/reset_data"
        )
    ),
    permission=is_global_admin,
).handle()
async def _(matcher: Matcher) -> None:
    await reset_from_update_file()
    await matcher.finish("数据已重写")


@on_command(
    "dump_data",
    state=dict(
        MatcherData(
            rm_name="导出数据", rm_desc="导出数据到json文件", rm_usage="/dump_data"
        )
    ),
    permission=is_global_admin,
).handle()
async def _(matcher: Matcher) -> None:
    await dump_to_json()
    await matcher.finish("数据已导出")
