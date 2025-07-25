from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment

from src.plugins.menu.models import MatcherData
from suggar_utils.blacklist.black import bl_manager
from suggar_utils.rule import is_global_admin
from suggar_utils.utils import send_forward_msg

black_list = on_command(
    "黑名单",
    aliases={"blacklist"},
    state=MatcherData(
        rm_name="列出黑名单", rm_desc="用于列出黑名单", rm_usage="/blacklist"
    ).model_dump(),
    permission=is_global_admin,
)


@black_list.handle()
async def _(bot: Bot, event: MessageEvent):
    group_blacklist = await bl_manager.get_group_blacklist()
    private_blacklist = await bl_manager.get_private_blacklist()
    group_list_str = "".join(f"群：{k} 原因：{v}\n" for k, v in group_blacklist.items())
    private_blacklist_str = "".join(
        f"用户：{k} 原因：{v}\n" for k, v in private_blacklist.items()
    )
    await send_forward_msg(
        bot,
        event,
        "黑名单列表",
        str(event.self_id),
        [
            MessageSegment.text(
                "⚠️ 群黑名单列表：" + (f"\n{group_list_str}" if group_list_str else "无")
            ),
            MessageSegment.text(
                "⚠️ 用户黑名单列表："
                + (f"\n{private_blacklist_str}" if private_blacklist_str else "无")
            ),
        ],
    )
