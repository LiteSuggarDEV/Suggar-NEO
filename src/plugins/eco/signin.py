import math
import random
from datetime import datetime

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.matcher import Matcher
from nonebot_plugin_value.api.api_balance import add_balance, get_or_create_account

from src.plugins.menu.models import MatcherData
from suggar_utils.store import get_fun_data, save_fun_data
from suggar_utils.utils import is_same_day
from suggar_utils.value import SUGGAR_EXP_ID, SUGGAR_VALUE_ID


@on_fullmatch(
    "签到",
    state=dict(
        MatcherData(
            rm_name="每日签到",
            rm_desc="签到",
            rm_usage="签到",
        )
    ),
).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    fun_data = get_fun_data(str(event.user_id))

    economy_data = await get_or_create_account(str(event.user_id))
    love_data = await get_or_create_account(str(event.user_id), SUGGAR_VALUE_ID)
    exp_data = await get_or_create_account(str(event.user_id), SUGGAR_EXP_ID)
    if is_same_day(int(fun_data.last_daily), int(datetime.now().timestamp())):
        await matcher.finish(
            MessageSegment.at(event.user_id)
            + MessageSegment.text(
                "今天已经签到过了喵～\n"
                + f"\n你的经验值：{int(exp_data.balance)}"
                + f"\n等级：{int(math.sqrt(exp_data.balance))}"
                + f"\n好感值：{int(love_data.balance)}"
                + f"\n货币：{economy_data.balance}点"
            )
        )
    love = float(random.randint(1, 10))
    coin = float(random.randint(1, 100))
    exp = float(random.randint(1, 50))
    fun_data.daily_count += 1
    fun_data.last_daily = datetime.now().timestamp()
    await add_balance(str(event.user_id), coin, "签到")
    await add_balance(str(event.user_id), love, "签到", SUGGAR_VALUE_ID)
    await add_balance(str(event.user_id), exp, "签到", SUGGAR_EXP_ID)
    formatted_datetime = datetime.fromtimestamp(int(fun_data.last_daily)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    save_fun_data(str(event.user_id), fun_data)
    await matcher.send(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(
            f" {formatted_datetime} 签到成功，累计签到{fun_data.daily_count}天~\n硬币+{coin}，经验+{exp}，好感度+{love}"
        )
    )
