import random
from collections import defaultdict
from datetime import datetime

from nonebot import get_driver, logger, on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.exception import NoneBotException
from nonebot.params import CommandArg
from nonebot_plugin_orm import AsyncSession, get_session
from nonebot_plugin_value.api.api_balance import add_balance, del_balance
from nonebot_plugin_value.uuid_lib import to_uuid
from sqlalchemy import select

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.config import config_manager
from suggar_utils.token_bucket import TokenBucket
from suggar_utils.utils import is_same_day, send_forward_msg

from .functions import add_fish_record, get_user_data_pyd, sell_fish
from .models import (
    FishMeta,
    QualityMetaData,
    UserFishMetaData,
)
from .pyd_models import Fish, QualityEnum
from .pyd_models import FishMeta as F_Meta

watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.fishing_rate_limit, capacity=1)
)

enchant = on_command(
    "鱼竿附魔",
    priority=10,
    block=True,
    state=dict(
        MatcherData(
            name="鱼竿附魔",
            usage="/鱼竿附魔",
            description="添加鱼竿附魔等级",
            category=CategoryEnum.GAME.value,
            params=[
                CommandParam(
                    name="种类",
                    description="附魔种类(海之眷顾，多重钓竿，自动打窝)",
                    param_type=ParamType.OPTIONAL,
                )
            ],
        )
    ),
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
            examples=["/卖鱼 稀有"],
            category=CategoryEnum.GAME.value,
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
    block=True,
    state=dict(
        MatcherData(
            name="钓鱼",
            category=CategoryEnum.GAME.value,
            description="钓鱼 来当赛博钓鱼佬吧～",
            usage="钓鱼",
        )
    ),
)
bag = on_fullmatch(
    ("背包", *[f"{prefix}背包" for prefix in get_driver().config.command_start]),
    priority=10,
    block=True,
    state=dict(
        MatcherData(
            name="背包",
            category=CategoryEnum.GAME.value,
            description="背包",
            usage="背包",
        )
    ),
)


async def do_fishing(
    event: MessageEvent,
    session: AsyncSession,
    probability_choose: float,
    feeding_level: int,
) -> Fish:
    quality_sequence = (await session.execute(select(QualityMetaData))).scalars().all()
    session.add_all(quality_sequence)
    quality_list = [q for q in quality_sequence if probability_choose <= q.probability]
    if not quality_list:
        quality = random.choice([q for q in quality_sequence if q.probability > 0.4])
    else:
        quality = random.choice(quality_list)
    stmt = select(FishMeta).where(FishMeta.quality == quality.name)
    fish_to_choose = (await session.execute(stmt)).scalars().all()
    session.add_all(fish_to_choose)
    fish_meta = random.choice(fish_to_choose)
    fish_meta_pyd = F_Meta.model_validate(fish_meta, from_attributes=True)
    fish = Fish(
        user_id=event.get_user_id(),
        length=int(
            float(random.randint(quality.length_range_start, quality.length_range_end))
            * (1.0 + 0.05 * feeding_level)
        ),
        time=datetime.now(),
        metadata=fish_meta_pyd,
    )
    await add_fish_record(event.user_id, fish)
    return fish


@enchant.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text()
    uid = to_uuid(event.get_user_id())
    async with get_session() as session:
        if not (
            user_meta := (
                await session.execute(
                    select(UserFishMetaData).where(UserFishMetaData.user_id == uid)
                )
            ).scalar_one_or_none()
        ):
            user_meta = UserFishMetaData(user_id=uid)
            session.add(user_meta)
            await session.commit()
            await session.refresh(user_meta)
        session.add(user_meta)
        match msg:
            case "":
                await enchant.finish(
                    f"{event.sender.nickname!s}({event.user_id!s})的附魔信息：\n"
                    + f"自动打窝：Level {user_meta.feeding!s}\n"
                    + f"海之眷顾：Level {user_meta.lucky_of_the_sea!s}\n"
                    + f"多重钓竿：Level {user_meta.multi_fish!s}"
                )
            case "海之眷顾":
                coast = 10000 * user_meta.lucky_of_the_sea + 2500
                try:
                    await del_balance(uid, coast)
                except Exception:
                    await enchant.finish(f"余额不足，需要{coast}")
                if user_meta.lucky_of_the_sea > 40:
                    await enchant.finish("海之眷顾已达最高等级")
                user_meta.lucky_of_the_sea += 1
                await session.commit()
                await session.refresh(user_meta)
                await enchant.finish(
                    f"已将海之眷顾提高到Level{user_meta.lucky_of_the_sea}，消耗{coast}金币"
                )
            case "多重钓竿":
                coast = 15000 * user_meta.multi_fish + 5000
                try:
                    await del_balance(uid, coast)
                except Exception:
                    await enchant.finish(f"余额不足，需要{coast}")
                if user_meta.multi_fish > 40:
                    await enchant.finish("多重钓竿已达最高等级")
                user_meta.multi_fish += 1
                await session.commit()
                await session.refresh(user_meta)
                await enchant.finish(
                    f"已将多重钓竿提高到Level {user_meta.multi_fish}，消耗{coast}金币"
                )
            case "自动打窝":
                coast = 7000 * user_meta.multi_fish + 4000
                try:
                    await del_balance(uid, coast)
                except Exception:
                    await enchant.finish("金币不足")
                if user_meta.feeding > 40:
                    await enchant.finish("自动打窝已达最高等级")
                user_meta.feeding += 1
                await session.commit()
                await session.refresh(user_meta)
                await enchant.finish(
                    f"已将自动打窝提高到Level {user_meta.feeding}，消耗{coast}金币"
                )
            case _:
                await enchant.finish("不理解的参数")


@sell.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()

    price = 0
    if not msg:
        await sell.finish("请输入要出售的鱼/特定品质的鱼")
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
    except Exception as e:
        await sell.send("发生错误，卖鱼失败了")
        logger.warning(e)


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

max_levels = {
    "lucky_of_the_sea": 40,  # 幸运属性上限
    "multi_fish": 40,  # 多重钓竿上限
    "feeding": 40,  # 自动打窝上限
}


@fishing.handle()
async def _(bot: Bot, event: MessageEvent):
    ins_id = str(event.user_id)
    bukkit = watch_user[ins_id]
    if not bukkit.consume():
        await fishing.finish("鱼竿过热了，休息一下吧......")

    await fishing.send("正在钓鱼......")
    uid = to_uuid(event.get_user_id())
    async with get_session() as session:
        try:
            result = await session.execute(
                select(UserFishMetaData).where(UserFishMetaData.user_id == uid)
            )
            if not (user_meta := result.scalar_one_or_none()):
                user_meta = UserFishMetaData(user_id=uid)
                session.add(user_meta)
                await session.commit()
                await session.refresh(user_meta)

            for attr, max_level in max_levels.items():
                if getattr(user_meta, attr) > max_level:
                    setattr(user_meta, attr, max_level)

            if user_meta.today_fishing_count >= config_manager.config.max_fishing_count:
                if is_same_day(
                    int(datetime.now().timestamp()),
                    int(user_meta.last_fishing_time.timestamp()),
                ):
                    await fishing.finish("今天的钓鱼次数已达上限，请明天再来！")
                else:
                    user_meta.today_fishing_count = 0
                    user_meta.last_fishing_time = datetime.now()
            luck_level = user_meta.lucky_of_the_sea
            multi_fish_level = user_meta.multi_fish
            feeding_level = user_meta.feeding

            probability_choose = ((random.randint(1, 10000)) / 10000) * (
                1 - 0.05 * luck_level
            )
            if probability_choose <= 0.05:
                probability_choose = 0.05
            if probability_choose == float(1):
                await fishing.finish("...鱼竿断了的说")
            elif probability_choose >= 0.9:
                await fishing.finish("...空军了")
            should_mutifish = random.randint(1, 100) <= multi_fish_level * 10
            fishes = [
                await do_fishing(event, session, probability_choose, feeding_level)
            ]
            if should_mutifish:
                fishes.extend(
                    [
                        await do_fishing(
                            event, session, probability_choose, feeding_level
                        )
                        for _ in range(
                            1,
                            int(0.4 * multi_fish_level)
                            if int(0.4 * multi_fish_level) > 1
                            else 1,
                        )
                    ]
                )
            user_meta.today_fishing_count += 1
            user_meta.last_fishing_time = datetime.now()
        except:
            raise
        else:
            await session.commit()
    await fishing.finish(
        MessageSegment.reply(event.message_id)
        + MessageSegment.text(
            "你钓到了 "
            + "".join(
                [
                    f"\n[{fish.metadata.quality}]{fish.metadata.name} 长度：{f'{fish.length!s}cm' if fish.length < 100 else f'{fish.length / 100:.2f}m'}\n"
                    + (f"{fish.metadata.prompt}\n" if fish.metadata.prompt else "")
                    for fish in fishes
                ]
            )
            + "了！\n"
            + "已收进你的背包～"
        )
    )
