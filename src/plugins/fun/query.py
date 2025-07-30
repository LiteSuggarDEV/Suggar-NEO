from nonebot import get_driver, on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot_plugin_value.api.api_balance import get_or_create_account

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.config import config_manager
from suggar_utils.value import SUGGAR_EXP_ID, to_uuid

command_start = get_driver().config.command_start


@on_command(
    "查询",
    block=True,
    state=dict(
        MatcherData(
            name="用户信息查询",
            description="查询一个人的等级信息～",
            usage="/查询",
            category=CategoryEnum.UTILS,
            params=[
                CommandParam(
                    name="用户",
                    description="要查询的用户",
                    param_type=ParamType.REQUIRED,
                )
            ],
            examples=[
                "/查询 123456",
                "/查询 @JohnRichard",
            ],
        )
    ),
).handle()
async def _(
    bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    admins = config_manager.config.admins
    if isinstance(event, PrivateMessageEvent):
        if event.user_id not in admins:
            return
    if not args.extract_plain_text().strip():
        for seg in args:
            if seg.type == "at":
                user_id: int = seg.data["qq"]
                break
        else:
            user_id = event.user_id
    elif args.extract_plain_text().strip().isdigit():
        user_id = int(args.extract_plain_text().strip())
    else:
        await matcher.finish("请告诉我你需要查询的用户！")
    if user_id == event.self_id:
        await matcher.finish("不知道呢～")
    if isinstance(event, GroupMessageEvent):
        group_members = [
            data["user_id"]
            for data in await bot.get_group_member_list(group_id=event.group_id)
        ]
        if user_id not in group_members and event.user_id not in admins:
            await matcher.finish("该用户不在本群内！")
    economy_data = await get_or_create_account(to_uuid(str(user_id)))
    exp_data = await get_or_create_account(to_uuid(str(user_id)), SUGGAR_EXP_ID)
    await matcher.finish(
        MessageSegment.text(
            f"喵呜～你好呀人类！\n用户：{user_id!s}"
            + f"\n你的经验值：{int(exp_data.balance)}"
            + f"\n货币：{economy_data.balance}点"
        )
    )


@on_fullmatch(
    "等级",
    rule=to_me(),
    block=True,
    state=dict(
        MatcherData(
            name="信息查询",
            description="查询你的等级～",
            usage="等级",
            category=CategoryEnum.FUN,
        )
    ),
).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    economy_data = await get_or_create_account(to_uuid(str(event.user_id)))
    exp_data = await get_or_create_account(to_uuid(str(event.user_id)), SUGGAR_EXP_ID)
    await matcher.finish(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(
            "\n喵呜～你好呀人类！"
            + f"\n你的经验值：{int(exp_data.balance)}"
            + f"\n货币：{economy_data.balance}点"
        )
    )


@on_fullmatch(
    "余额",
    state=dict(
        MatcherData(
            name="信息查询",
            description="查询你的余额～",
            usage="余额",
            category=CategoryEnum.FUN,
        )
    ),
).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    economy_data = await get_or_create_account(to_uuid(str(event.user_id)))
    await matcher.finish(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(f"\n货币余额：{economy_data.balance}点")
    )
