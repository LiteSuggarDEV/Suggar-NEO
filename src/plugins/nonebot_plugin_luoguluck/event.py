import pickle
from datetime import datetime
from pathlib import Path

from aiofiles import open
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot_plugin_localstore import get_plugin_data_dir

from src.plugins.menu.models import CategoryEnum, MatcherData

from .image import get_image

data_path = Path(get_plugin_data_dir())

luck = on_command(
    "luck",
    aliases={"luck", "lucky", "运势"},
    priority=10,
    block=True,
    state=dict(
        MatcherData(
            name="今日运势",
            usage="/luck",
            description="洛谷同款的今日运势！",
            category=CategoryEnum.FUN,
        ),
    ),
)


async def is_same_day(timestamp1: int, timestamp2: int) -> bool:
    # 将时间戳转换为datetime对象，并只保留日期部分
    date1 = datetime.fromtimestamp(timestamp1).date()
    date2 = datetime.fromtimestamp(timestamp2).date()

    # 比较两个日期是否相同
    return date1 == date2


@luck.handle()
async def _(ev: MessageEvent, bot: Bot):
    global data_path
    nickname = ""
    user_id = ev.user_id

    if isinstance(ev, PrivateMessageEvent):
        event = ev
        nickname: str = event.sender.nickname if event.sender.nickname else "你"
    elif isinstance(ev, GroupMessageEvent):
        event = ev
        group_id = event.group_id
        info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        nickname: str = info["card"]

    if not data_path.exists():
        data_path.mkdir()

    user_conf = data_path / f"{user_id}.pickle"
    timestamp = datetime.now().timestamp()

    if not user_conf.exists():
        image = get_image(nickname)
        async with open(str(user_conf), "wb") as f:
            await f.seek(0)
            await f.write(pickle.dumps({"last_time": timestamp, "image": image}))

    else:
        async with open(str(user_conf), "rb") as f:
            await f.seek(0)
            data = pickle.loads(await f.read())

        if await is_same_day(int(timestamp), data["last_time"]):
            image = data["image"]
        else:
            image = get_image(nickname)
            async with open(str(user_conf), "wb") as f:
                await f.seek(0)
                await f.write(pickle.dumps({"last_time": timestamp, "image": image}))

    if isinstance(event, PrivateMessageEvent):
        await luck.send(MessageSegment.image(image))
    else:
        await luck.send(MessageSegment.at(user_id) + MessageSegment.image(image))
