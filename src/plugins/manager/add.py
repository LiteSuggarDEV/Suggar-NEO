from nonebot import on_request
from nonebot.adapters.onebot.v11 import (
    Bot,
    FriendRequestEvent,
    GroupRequestEvent,
    RequestEvent,
)

from suggar_utils.blacklist.black import bl_manager
from suggar_utils.utils import send_to_admin


@on_request().handle()
async def _(event: RequestEvent, bot: Bot):
    if isinstance(event, FriendRequestEvent):
        if await bl_manager.is_private_black(str(event.user_id)):
            await send_to_admin(f"尝试拒绝添加黑名单用户{event.user_id}.......")
            await event.reject(bot)
        else:
            await event.approve(bot=bot)
            await send_to_admin(f"收到{event.user_id}的好友请求：{event.comment or ''}")
    elif isinstance(event, GroupRequestEvent):
        if await bl_manager.is_private_black(str(event.user_id)):
            await send_to_admin(
                f"尝试拒绝添加黑名单用户{event.user_id}的拉群请求......."
            )
            await event.reject(bot)
            return
        elif await bl_manager.is_group_black(str(event.group_id)):
            await send_to_admin(
                f"尝试拒绝添加黑名单群组{event.group_id}的拉群请求......."
            )
            await event.reject(bot)
            return
        flag = event.flag
        # 获取LiteBot的群组列表
        group_list = await bot.get_group_list()
        group_joins = [int(group["group_id"]) for group in group_list]
        if event.sub_type != "invite":
            return
        if event.group_id not in group_joins:
            await send_to_admin(
                f"收到{event.user_id}加入群组邀请，已自动加入群组{event.group_id}"
            )
            await bot.set_group_add_request(approve=True, sub_type="invite", flag=flag)
