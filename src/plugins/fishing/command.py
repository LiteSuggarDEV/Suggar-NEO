import random
from collections import defaultdict
from datetime import datetime

from nonebot import get_driver, on_fullmatch, on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.exception import NoneBotException
from nonebot.params import CommandArg
from nonebot_plugin_orm import get_session
from nonebot_plugin_value.api.api_balance import add_balance
from nonebot_plugin_value.uuid_lib import to_uuid
from sqlalchemy import select

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.config import config_manager
from suggar_utils.token_bucket import TokenBucket
from suggar_utils.utils import send_forward_msg

from .functions import add_fish_record, get_user_data_pyd, sell_fish
from .models import (
    FishMeta,
    QualityMetaData,
)
from .pyd_models import Fish, QualityEnum
from .pyd_models import FishMeta as F_Meta

watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.fishing_rate_limit, capacity=1)
)

sell = on_message(
    priority=5,
    block=True,
    state=dict(
        MatcherData(
            name="卖鱼",
            description="卖鱼",
            usage="卖鱼 <鱼名>/<品质名>",
            examples=["卖鱼 稀有"],
            category=CategoryEnum.FUN,
            params=[
                CommandParam(
                    name="fish-name",
                    description="鱼名",
                    param_type=ParamType.OPTIONAL,
                ),
                CommandParam(
                    name="quality-name",
                    description="品质名",
                    param_type=ParamType.OPTIONAL,
                ),
            ],
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
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    for i in (
        "卖鱼",
        *[f"{prefix}卖鱼" for prefix in get_driver().config.command_start],
    ):
        if event.message.extract_plain_text().strip().startswith(i):
            break
    else:
        sell.skip()

    price = 0
    if not msg:
        await sell.send("请输入要出售的鱼/特定品质的鱼")
    if msg == QualityEnum.UNKNOWN.value:
        await sell.finish("这个不能出售哦")
    try:
        if price := await sell_fish(event.user_id, fish_name=msg):
            await sell.send(f"成功出售所有 {msg}，获得{price}金币")
        elif price := await sell_fish(event.user_id, quality_name=msg):
            await sell.send(f"成功出售所有{msg}品质的鱼，获得{price}金币")
        else:
            await sell.finish("没有这个品质/名字的鱼")
        await add_balance(to_uuid(event.get_user_id()), price, "卖鱼")
    except NoneBotException:
        raise
    except Exception:
        await sell.send("发生错误，卖鱼失败了")
        raise


@bag.handle()
async def _(bot: Bot, event: MessageEvent):
    data = await get_user_data_pyd(event.user_id)
    msg_list = [
        MessageSegment.text(f"{event.sender.nickname!s}({event.get_user_id()})的背包：")
    ]
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
    for quality in QualityEnum:
        if quality_data := quality_dict.get(quality.value):
            msg = f"==={quality}品质===\n"
            for fish_name, fish_data in quality_data.items():
                msg += (
                    f"{fish_name}：{fish_data['count']}条，总长度"
                    + f"""{str(fish_data["length"]) + "cm" if fish_data["length"] < 100 else (f"{fish_data['length'] / 100:.2f}m")}\n"""
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
        probability_choose = (random.randint(1, 10000)) / 10000
        if probability_choose == float(1):
            await fishing.finish("...鱼竿断了的说")
        elif probability_choose >= 0.9:
            await fishing.finish("...空军了")
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
            + f"\n长度：{f'{fish.length!s}cm' if fish.length < 100 else f'{fish.length / 100:.2f}m'}\n"
            + (f"{fish.metadata.prompt}\n" if fish.metadata.prompt else "")
            + "已收进你的背包～"
        )
    )
