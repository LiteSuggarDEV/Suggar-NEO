from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..check_rule import is_group_admin
from ..utils import get_memory_data, write_memory_data


async def switch(
    event: GroupMessageEvent, matcher: Matcher, bot: Bot, args: Message = CommandArg()
):
    if not await is_group_admin(event, bot):
        await matcher.finish("权限不足")
    arg = args.extract_plain_text().strip()
    data = await get_memory_data(event)
    if arg in ("开启", "on", "启用", "enable"):
        if not data.get("fake_people"):
            data["fake_people"] = True
            await write_memory_data(event, data)
            await matcher.send("开启FakePeople")
        else:
            await matcher.send("已开启")
    elif arg in ("关闭", "off", "禁用", "disable"):
        if data.get("fake_people", True):
            data["fake_people"] = False
            await write_memory_data(event, data)
            await matcher.send("关闭FakePeople")
        else:
            await matcher.send("已关闭")
    else:
        await matcher.send("请输入开启或关闭")
