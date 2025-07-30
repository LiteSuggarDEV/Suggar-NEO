from nonebot.adapters.onebot.v11 import Bot
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor

from suggar_utils.blacklist.black import bl_manager
from suggar_utils.event import GroupEvent, UserIDEvent
from suggar_utils.utils import send_to_admin


@run_preprocessor
async def message_preprocessor(matcher: Matcher, bot: Bot, event: UserIDEvent):
    if isinstance(event, GroupEvent) and await bl_manager.is_group_black(
        str(event.group_id)
    ):
        await send_to_admin(f"尝试退出黑名单群组{event.group_id}.......")
        await bot.set_group_leave(group_id=event.group_id)
        matcher.stop_propagation()
    if await bl_manager.is_private_black(str(event.user_id)):
        matcher.stop_propagation()
