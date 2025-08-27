from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_orm import get_session

require("amrita.plugins.menu")
from amrita.plugins.menu.models import MatcherData

from suggar_utils.rule import is_global_admin
from suggar_utils.store import to_uuid
from suggar_utils.switch_models import FuncEnum, get_or_create_switch

__plugin_meta__ = PluginMetadata(
    name="Manager扩展",
    description="适用于Suggar-NEO的Amrita Manager扩展插件",
    usage="",
    type="application",
    supported_adapters={"~onebot.v11"},
)

func_switch = on_command(
    "设置功能",
    aliases={"set_func"},
    permission=GROUP_ADMIN | GROUP_OWNER | is_global_admin,
    priority=10,
    block=True,
    state=MatcherData(
        usage="/set_func [功能名称] [功能状态]",
        description="设置功能状态",
        name="功能开关",
    ).model_dump(),
)


@func_switch.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text().strip().split()
    if len(msg) < 1:
        await func_switch.finish(
            "请提供功能名称和状态，例如：/set_func fishing on"
            + f"\n可用：{', '.join(list(FuncEnum.__members__))}"
        )
    if msg[0] not in FuncEnum.__members__:
        await func_switch.finish(
            f"功能名称错误，请使用以下功能：{', '.join(list(FuncEnum.__members__))}"
        )
    func: str = getattr(FuncEnum, msg[0]).value
    if not len(msg) >= 2:
        async with get_session() as session:
            group = await get_or_create_switch(to_uuid(str(event.group_id)), session)
            await func_switch.finish(f"{func} 当前状态为 {getattr(group, func)!s}")
    match msg[1].lower():
        case "on" | "enable" | "true" | "1" | "开启":
            status = True
        case "off" | "disable" | "false" | "0" | "关闭":
            status = False
        case _:
            await func_switch.finish(
                "功能状态错误，请使用 on/off 或 enable/disable 或 true/false"
            )
    group_id = to_uuid(str(event.group_id))
    async with get_session() as session:
        group = await get_or_create_switch(group_id, session)
        session.add(group)
        setattr(group, func, status)
        await session.commit()
    await func_switch.finish(f"{func} 已设置为 {status!s}")
