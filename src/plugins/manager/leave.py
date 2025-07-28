from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.rule import is_global_admin
from suggar_utils.utils import send_to_admin


@on_command(
    "set_leave",
    permission=is_global_admin,
    state=MatcherData(
        name="退出指定聊群",
        description="用于退出聊群",
        usage="/set_leave [<group-id>|--this]",
        category=CategoryEnum.MANAGE,
        params=[
            CommandParam(
                name="group-id",
                description="群号或--this",
                param_type=ParamType.REQUIRED,
            )
        ],
        examples=[
            "/set_leave 123456789",
            "/set_leave --this",
        ],
    ).model_dump(),
).handle()
async def leave(
    bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()
):
    str_id = arg.extract_plain_text().strip()
    if isinstance(event, GroupMessageEvent):
        if not str_id:
            await matcher.finish("⚠️ 请输入--this来离开这个群！或者指定群号！")
        if str_id == "--this":
            await send_to_admin(f"⚠️ 尝试离开群：{event.group_id}")
            await matcher.send("✅ 已退出本群！")
            await bot.set_group_leave(group_id=event.group_id)
    if str_id != "--this":
        try:
            int(str_id)
        except Exception:
            await matcher.finish("⚠️ 请输入一个数字")
        else:
            await matcher.send(f"⚠️ 尝试离开{str_id}")
            await bot.set_group_leave(group_id=int(str_id))
    else:
        await matcher.finish("⚠️ 该参数只允许在群内使用！")
