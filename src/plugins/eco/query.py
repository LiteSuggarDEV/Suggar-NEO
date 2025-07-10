from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import to_me
from nonebot_plugin_value.api.api_balance import get_or_create_account

from src.plugins.menu.models import MatcherData
from suggar_utils.store import get_fun_data
from suggar_utils.value import SUGGAR_VALUE_ID


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
    fun_data = get_fun_data(str(event.user_id))
    ecommony_data = await get_or_create_account(str(event.user_id))
    love_data = await get_or_create_account(str(event.user_id), SUGGAR_VALUE_ID)
    await matcher.finish(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(
            "\n喵呜～你好呀人类！"
            + f"\n你的经验值：{fun_data.exp}"
            + f"\n好感值：{int(love_data.balance)}"
            + f"\n货币：{ecommony_data.balance}点"
        )
    )
