from nonebot import on_command
from nonebot.matcher import Matcher

from src.plugins.menu.models import CategoryEnum, MatcherData
from suggar_utils.dump_tools import dump_to_json, reset_from_update_file
from suggar_utils.rule import is_global_admin


@on_command(
    "reset_data",
    state=dict(
        MatcherData(
            name="重写数据",
            description="从恢复文件重置数据",
            usage="/reset_data",
            category=CategoryEnum.MANAGE,
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
            name="导出数据",
            description="导出数据到json文件",
            usage="/dump_data",
            category=CategoryEnum.MANAGE,
        )
    ),
    permission=is_global_admin,
).handle()
async def _(matcher: Matcher) -> None:
    await dump_to_json()
    await matcher.finish("数据已导出")
