import math
import random
from datetime import datetime

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.matcher import Matcher
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import get_or_create_account

from src.plugins.menu.models import MatcherData
from suggar_utils.store import get_or_create_user_model
from suggar_utils.utils import is_same_day
from suggar_utils.value import SUGGAR_EXP_ID, add_balance, to_uuid


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
    economy_data = await get_or_create_account(to_uuid(str(event.user_id)))
    exp_data = await get_or_create_account(to_uuid(str(event.user_id)), SUGGAR_EXP_ID)
    async with get_session() as session:
        fun_data = await get_or_create_user_model(str(event.user_id), session)
        session.add(fun_data)
        last_daily = fun_data.last_daily
        if is_same_day(int(last_daily.timestamp()), int(datetime.now().timestamp())):
            await matcher.finish(
                MessageSegment.at(event.user_id)
                + MessageSegment.text(
                    "\n今天已经签到过了喵～\n"
                    + f"\n你的经验值：{int(exp_data.balance)}"
                    + f"\n等级：{int(math.sqrt(exp_data.balance))}"
                    + f"\n货币：{economy_data.balance}点"
                )
            )
        coin = float(random.randint(1, 100))
        exp = float(random.randint(1, 50))
        daily_count = fun_data.daily_count
        daily_count += 1
        fun_data.daily_count = daily_count
        fun_data.last_daily = datetime.now()

        await session.commit()
    await add_balance(str(event.user_id), coin, "签到")
    await add_balance(str(event.user_id), exp, "签到", SUGGAR_EXP_ID)
    formatted_datetime = last_daily.strftime("%Y-%m-%d %H:%M:%S")
    await matcher.send(
        MessageSegment.at(event.user_id)
        + MessageSegment.text(
            f"\n {formatted_datetime} 签到成功，累计签到{daily_count}天~\n硬币+{coin}，经验+{exp}"
        )
    )
