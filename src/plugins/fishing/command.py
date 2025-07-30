import random
from collections import defaultdict
from datetime import datetime

from nonebot import get_driver, on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import add_balance
from nonebot_plugin_value.uuid_lib import to_uuid
from sqlalchemy import select

from src.plugins.menu.models import CategoryEnum, MatcherData
from suggar_utils.config import config_manager
from suggar_utils.token_bucket import TokenBucket
from suggar_utils.utils import send_forward_msg

from .functions import add_fish_record, get_user_data_pyd, sell_fish
from .models import (
    FishMeta,
    QualityMetaData,
)
from .pyd_models import Fish
from .pyd_models import FishMeta as F_Meta

watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.fishing_rate_limit, capacity=1)
)

sell = on_command(
    "卖鱼",
    priority=10,
    block=True,
    state=dict(
        MatcherData(
            name="/卖鱼",
            description="卖鱼",
            usage="/卖鱼 <鱼名>/<品质名>",
        )
    ),
)

fishing = on_fullmatch(
    ("钓鱼", *[f"{prefix}钓鱼" for prefix in get_driver().config.command_start]),
    priority=10,
    state=dict(
        MatcherData(
            name="钓鱼",
            category=CategoryEnum.FUN,
            description="钓鱼 来当赛博钓鱼佬吧～",
            usage="钓鱼",
        )
    ),
)
bag = on_fullmatch(
    ("背包", *[f"{prefix}背包" for prefix in get_driver().config.command_start]),
    priority=10,
    state=dict(
        MatcherData(
            name="背包",
            category=CategoryEnum.FUN,
            description="背包",
            usage="背包",
        )
    ),
)


@sell.handle()
async def _(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text().strip()
    price = 0
    try:
        if price := await sell_fish(event.user_id, fish_name=msg):
            await sell.send(f"成功出售所有 {msg}，获得{price}金币")
        elif price := await sell_fish(event.user_id, quality_name=msg):
            await sell.send(f"成功出售所有{msg}品质的鱼，获得{price}金币")
        else:
            await sell.finish("没有这个品质/名字的鱼")
        await add_balance(to_uuid(event.get_user_id()), price, "卖鱼")
    except Exception:
        await sell.send("发生错误，卖鱼失败了")
        raise

@bag.handle()
async def _(bot: Bot, event: MessageEvent):
    data = await get_user_data_pyd(event.user_id)
    msg_list = []
    quality_dict: dict[str, dict[str, dict[str, int]]] = {}
    for fish in data.fishes:
        if fish.metadata.quality not in quality_dict:
            quality_dict[fish.metadata.quality] = {}
        if fish.metadata.name in quality_dict[fish.metadata.quality]:
            quality_dict[fish.metadata.quality][fish.metadata.name]["count"] += 1
            quality_dict[fish.metadata.quality][fish.metadata.name]["length"] += (
                fish.length
            )
        else:
            quality_dict[fish.metadata.quality][fish.metadata.name] = {
                "count": 1,
                "length": fish.length,
            }
    for quality, quality_data in quality_dict.items():
        msg = f"==={quality}品质===\n"
        for fish_name, fish_data in quality_data.items():
            msg += (
                f"{fish_name}：{fish_data['count']}条，总长度"
                + f"""{str(fish_data["length"]) + "cm" if fish_data["length"] < 100 else (f"{(fish_data['length'] / 100)!s:.2f}m")}\n"""
            )
        msg_list.append(MessageSegment.text(msg))
    await send_forward_msg(
        bot,
        event,
        config_manager.config.bot_name,
        str(event.self_id),
        msg_list,
    )


@fishing.handle()
async def _(bot: Bot, event: MessageEvent):
    ins_id = str(event.user_id)
    bukkit = watch_user[ins_id]
    if not bukkit.consume():
        await fishing.finish("鱼竿过热了，休息一下吧......")
    await fishing.send("正在钓鱼......")
    async with get_session() as session:
        quality_sequence = (
            (await session.execute(select(QualityMetaData))).scalars().all()
        )
        session.add_all(quality_sequence)
        probability_choose = (random.randint(1, 100)) / 100
        if probability_choose == float(1):
            await fishing.finish("...鱼竿折断了的说")
        quality_list = [
            q for q in quality_sequence if probability_choose <= q.probability
        ]
        if not quality_list:
            quality = random.choice(
                [q for q in quality_sequence if q.probability > 0.4]
            )
        else:
            quality = random.choice(quality_list)
        stmt = select(FishMeta).where(FishMeta.quality == quality.name)
        fish_to_choose = (await session.execute(stmt)).scalars().all()
        session.add_all(fish_to_choose)
        fish_meta = random.choice(fish_to_choose)
        fish_meta_pyd = F_Meta.model_validate(fish_meta, from_attributes=True)
        fish = Fish(
            user_id=event.get_user_id(),
            length=random.randint(quality.length_range_start, quality.length_range_end),
            time=datetime.now(),
            metadata=fish_meta_pyd,
        )
        await add_fish_record(event.user_id, fish)
    await fishing.finish(
        MessageSegment.reply(event.message_id)
        + MessageSegment.text(
            f"你钓到了 [{fish.metadata.quality}]{fish.metadata.name} 了！"
            + f"\n长度：{f'{fish.length!s}cm' if fish.length < 100 else f'{fish.length / 100:.2f}m'}\n已收进你的背包～"
        )
    )
