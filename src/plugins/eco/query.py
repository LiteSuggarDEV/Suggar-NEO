from nonebot import get_driver, on_fullmatch, on_startswith
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

from src.plugins.menu.models import MatcherData
from suggar_utils.config import ConfigManager
from suggar_utils.value import SUGGAR_EXP_ID, SUGGAR_VALUE_ID

command_start = get_driver().config.command_start


@on_startswith(
    ("查询", *(f"{prefix}查询" for prefix in command_start)),
    block=True,
    state=dict(
        MatcherData(
            rm_name="用户信息查询",
            rm_desc="查询一个人的等级信息～",
            rm_usage="查询 @用户",
        )
    ),
).handle()
async def _(
    bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    admins = ConfigManager().get_config().admins
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
    economy_data = await get_or_create_account(str(user_id))
    love_data = await get_or_create_account(str(user_id), SUGGAR_VALUE_ID)
    exp_data = await get_or_create_account(str(user_id), SUGGAR_EXP_ID)
    await matcher.finish(
        MessageSegment.text(
            f"喵呜～你好呀人类！\n用户：{user_id!s}"
            + f"\n你的经验值：{int(exp_data.balance)}"
            + f"\n好感值：{int(love_data.balance)}"
            + f"\n货币：{economy_data.balance}点"
        )
    )


@on_fullmatch(
    "等级",
    rule=to_me(),
    block=True,
    state=dict(
        MatcherData(
            rm_name="信息查询",
            rm_desc="查询你的等级～",
            rm_usage="等级",
        )
    ),
).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    economy_data = await get_or_create_account(str(event.user_id))
    love_data = await get_or_create_account(str(event.user_id), SUGGAR_VALUE_ID)
    exp_data = await get_or_create_account(str(event.user_id), SUGGAR_EXP_ID)
    await matcher.finish(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(
            "\n喵呜～你好呀人类！"
            + f"\n你的经验值：{int(exp_data.balance)}"
            + f"\n好感值：{int(love_data.balance)}"
            + f"\n货币：{economy_data.balance}点"
        )
    )


@on_fullmatch(
    "余额",
    state=dict(
        MatcherData(
            rm_name="信息查询",
            rm_desc="查询你的余额～",
            rm_usage="余额",
        )
    ),
).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    economy_data = await get_or_create_account(str(event.user_id))
    await matcher.finish(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(f"\n货币余额：{economy_data.balance}点")
    )
