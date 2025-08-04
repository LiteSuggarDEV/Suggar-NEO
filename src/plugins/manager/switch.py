
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot_plugin_orm import get_session

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.store import to_uuid
from suggar_utils.switch_models import FuncEnum, get_or_create_switch

func_switch = on_command(
    "设置功能",
    aliases={"set_func"},
    permission=GROUP_ADMIN | GROUP_OWNER,
    priority=10,
    block=True,
    state=MatcherData(
        category=CategoryEnum.MANAGE,
        params=[
            CommandParam(
                name="功能名称",
                description="功能名称",
                param_type=ParamType.REQUIRED,
            ),
            CommandParam(
                name="功能状态",
                description="功能状态",
                param_type=ParamType.REQUIRED,
            ),
        ],
        usage="/set_func [功能名称] [功能状态]",
        description="设置功能状态",
        name="功能开关",
    ).model_dump(),
)


@func_switch.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text().strip().split()
    if len(msg) != 2:
        await func_switch.finish(
            "请提供功能名称和状态，例如：/set_func fishing on"
            + f"\n可用：{', '.join([e.value for e in FuncEnum])}"
        )
    if msg[0] not in FuncEnum.__members__:
        await func_switch.finish(
            f"功能名称错误，请使用以下功能：{', '.join([e.value for e in FuncEnum])}"
        )
    func = FuncEnum[msg[0]].value
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
        setattr(group, func, status)
        await session.commit()
        await func_switch.finish(f"{func} 已设置为 {status!s}")
