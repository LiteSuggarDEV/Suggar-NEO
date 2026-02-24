import random

from amrita_core import CompletionEvent, on_completion
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent

from suggar_utils.value import SUGGAR_EXP_ID, add_balance


@on_completion(block=False).handle()
async def _(event: CompletionEvent, nonebot_event: MessageEvent) -> None:
    assert isinstance(nonebot_event, MessageEvent)
    exp = float(random.randint(1, 15))
    coin = float(random.randint(1, 10))
    await add_balance(nonebot_event.get_user_id(), exp, "聊天", SUGGAR_EXP_ID)
    await add_balance(nonebot_event.get_user_id(), coin, "聊天")
    logger.debug(f"用户{nonebot_event.user_id}获得{exp}经验值和{coin}金币")
