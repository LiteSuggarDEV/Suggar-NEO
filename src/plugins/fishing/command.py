import random
from collections import defaultdict
from datetime import datetime
from math import sqrt

from nonebot import MatcherGroup, get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.exception import NoneBotException
from nonebot.params import CommandArg
from nonebot_plugin_orm import AsyncSession, get_session
from nonebot_plugin_value.api.api_balance import (
    add_balance,
    del_balance,
    get_or_create_account,
)
from nonebot_plugin_value.exception import TransactionException
from nonebot_plugin_value.uuid_lib import to_uuid
from sqlalchemy import select

from src.plugins.menu.models import CategoryEnum, CommandParam, MatcherData, ParamType
from suggar_utils.config import config_manager
from suggar_utils.switch_models import FuncEnum, is_enabled
from suggar_utils.token_bucket import TokenBucket
from suggar_utils.utils import is_same_day, send_forward_msg

from .functions import (
    add_fish_record,
    get_or_create_user_model,
    get_user_data_pyd,
    get_user_progress,
    refresh_progress,
    sell_fish,
)
from .models import FishMeta, QualityMetaData
from .pyd_models import FISHING_POINT, Fish, QualityEnum
from .pyd_models import FishMeta as F_Meta

#  常量配置
MAX_ENCHANT_LEVEL = 40  # 附魔等级上限
ENCHANT_COST_FACTORS = {
    "海之眷顾": (10000, 2500),
    "多重钓竿": (15000, 5000),
    "自动打窝": (7000, 4000),
}
MIN_PROBABILITY = 0.01
base_matcher = MatcherGroup(rule=is_enabled(FuncEnum.FISHING))


#  辅助函数
def format_length(length: int) -> str:
    """格式化鱼的长度显示"""
    if length < 100:
        return f"{length}cm"
    elif length < 100000:
        return f"{length / 100:.2f}m"
    else:
        return f"{length / 100000:.2f}km"


def calculate_enchant_cost(level: int, enchant_type: str) -> int:
    """计算附魔升级消耗"""
    base, extra = ENCHANT_COST_FACTORS[enchant_type]
    return base * level + extra


async def perform_fishing(
    event: MessageEvent,
    session: AsyncSession,
    probability: float,
    feeding_level: int,
) -> Fish:
    """执行一次钓鱼操作"""
    async with session:
        # 获取所有品质并按概率过滤
        qualities = (await session.scalars(select(QualityMetaData))).all()
        valid_qualities = [q for q in qualities if probability <= q.probability].sort(
            key=lambda q: q.probability, reverse=True
        )

        # 选择品质
        quality = (
            random.choice(valid_qualities)
            if valid_qualities
            else random.choice([q for q in qualities if q.probability > 0.01])
        )

        # 选择鱼种
        fish_to_choose = (
            await session.scalars(
                select(FishMeta).where(FishMeta.quality == quality.name)
            )
        ).all()
        fish_meta = random.choice(fish_to_choose)

        # 计算鱼长度
        length = random.randint(quality.length_range_start, quality.length_range_end)
        length = int(length * (1 + 0.05 * feeding_level))

        # 创建鱼对象
        fish = Fish(
            user_id=event.get_user_id(),
            length=length,
            time=datetime.now(),
            metadata=F_Meta.model_validate(fish_meta, from_attributes=True),
        )

    try:
        await add_fish_record(event.user_id, fish)
    except Exception as e:
        logger.warning(f"保存鱼记录失败: {e}")
        raise  # 重新抛出异常以便外层处理

    return fish


#  命令处理器
watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.fishing.rate_limit, capacity=1)
)

# 鱼竿附魔命令
enchant_matcher_data = MatcherData(
    name="/鱼竿附魔",
    usage="/鱼竿附魔",
    aliases=["/enchant"],
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
enchant = base_matcher.on_command(
    "鱼竿附魔",
    aliases={"enchant"},
    priority=10,
    block=True,
    state=enchant_matcher_data.model_dump(),
)

# 卖鱼命令
sell_matcher_data = MatcherData(
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
sell = base_matcher.on_command(
    "卖鱼", priority=10, block=True, state=sell_matcher_data.model_dump()
)

to_money_matcher_data = MatcherData(
    name="/兑换货币",
    description="兑换货币",
    usage="/兑换货币 <数量>",
    examples=["/兑换货币 100"],
    category=CategoryEnum.GAME.value,
    params=[
        CommandParam(
            name="amount",
            description="兑换数量",
            param_type=ParamType.OPTIONAL,
        )
    ],
)
to_money = base_matcher.on_command(
    "兑换货币", priority=10, block=True, state=to_money_matcher_data.model_dump()
)
points_matcher_data = MatcherData(
    name="/钓鱼积分",
    description="查看钓鱼积分",
    usage="/钓鱼积分",
    examples=["/钓鱼积分"],
    category=CategoryEnum.GAME.value,
)
points = base_matcher.on_command(
    "钓鱼积分",
    priority=10,
    block=True,
    state=points_matcher_data.model_dump(),
)

# 钓鱼命令
fishing_matcher_data = MatcherData(
    name="钓鱼",
    category=CategoryEnum.GAME.value,
    description="钓鱼 来当赛博钓鱼佬吧～",
    usage="钓鱼",
)
command_starts = [f"{prefix}钓鱼" for prefix in get_driver().config.command_start]
fishing = base_matcher.on_fullmatch(
    ("钓鱼", *command_starts),
    priority=10,
    block=True,
    state=fishing_matcher_data.model_dump(),
)

# 背包命令
bag_matcher_data = MatcherData(
    name="背包", category=CategoryEnum.GAME.value, description="背包", usage="背包"
)
bag = base_matcher.on_fullmatch(
    ("背包", *[f"{prefix}背包" for prefix in get_driver().config.command_start]),
    priority=10,
    block=True,
    state=bag_matcher_data.model_dump(),
)

progress_matcher_data = MatcherData(
    name="钓鱼进度",
    category=CategoryEnum.GAME.value,
    description="钓鱼进度",
    usage="/钓鱼进度",
)
progress = base_matcher.on_fullmatch(
    (
        "钓鱼进度",
        *[f"{prefix}钓鱼进度" for prefix in get_driver().config.command_start],
    ),
    priority=10,
    block=True,
    state=progress_matcher_data.model_dump(),
)

@points.handle()
async def _(bot: Bot, event: MessageEvent):
    uid = to_uuid(event.get_user_id())
    try:
        account = await get_or_create_account(uid, FISHING_POINT.id)
        balance = account.balance
    except Exception as e:
        await points.finish(
            f"获取钓鱼积分时发生错误: {str(e)}"
        )
        return
    await points.finish(
        f"{event.sender.nickname}({event.get_user_id()})的钓鱼积分为{balance}。"
    )


@to_money.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    uid = to_uuid(event.get_user_id())
    if not msg:
        await to_money.finish(
            f"请输入兑换数量，当前兑换比例为1:10000，您的钓鱼积分为{(await get_or_create_account(uid, FISHING_POINT.id)).balance}。"
        )
    if not msg.isdigit():
        return await to_money.finish("请输入有效的数字")

    amount = int(msg)
    if amount <= 0:
        await to_money.finish("兑换数量必须大于0")
    if amount < 10000:
        await to_money.finish("兑换数量过小")
    try:
        await del_balance(uid, amount, "兑换货币", FISHING_POINT.id)
        await add_balance(uid, amount / 10000, "兑换货币")
        await to_money.finish(f"成功兑换{amount / 10000}金币，消耗{amount}钓鱼积分")
    except TransactionException:
        await to_money.finish("你没有那么多的钓鱼积分")


#  命令处理逻辑
@enchant.handle()
async def handle_enchant(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    uid = to_uuid(event.get_user_id())

    async with get_session() as session:
        user_meta = await get_or_create_user_model(event.user_id, session)

        # 显示当前附魔信息
        if not msg:
            return await enchant.finish(
                f"{event.sender.nickname}({event.user_id})的附魔信息：\n"
                f"自动打窝：Level {user_meta.feeding}\n"
                f"海之眷顾：Level {user_meta.lucky_of_the_sea}\n"
                f"多重钓竿：Level {user_meta.multi_fish}"
            )

        # 处理附魔升级
        enchant_handlers = {
            "海之眷顾": ("lucky_of_the_sea", "海之眷顾"),
            "多重钓竿": ("multi_fish", "多重钓竿"),
            "自动打窝": ("feeding", "自动打窝"),
        }

        if msg in enchant_handlers:
            attr_name, display_name = enchant_handlers[msg]
            current_level = getattr(user_meta, attr_name)

            # 检查等级上限
            if current_level >= MAX_ENCHANT_LEVEL:
                return await enchant.finish(f"{display_name}已达最高等级")

            # 计算消耗并扣款
            cost = calculate_enchant_cost(current_level, display_name)
            try:
                await del_balance(uid, cost, "附魔", currency_id=FISHING_POINT.id)
            except Exception:
                return await enchant.finish(f"余额不足，需要{cost}积分")

            # 升级属性
            setattr(user_meta, attr_name, current_level + 1)
            await session.commit()
            await session.refresh(user_meta)
            await enchant.finish(
                f"已将{display_name}提高到Level {getattr(user_meta, attr_name)}，消耗{cost}积分"
            )
        else:
            await enchant.finish("不支持的附魔类型")


@sell.handle()
async def handle_sell(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()

    if not msg:
        return await sell.finish("请输入要出售的鱼/特定品质的鱼")

    if msg == QualityEnum.UNKNOWN.value:
        return await sell.finish("这个不能出售哦")

    try:
        # 尝试按鱼名出售
        price = await sell_fish(event.user_id, fish_name=msg)
        if price:
            await sell.send(f"成功出售所有 {msg}，获得{price}钓鱼积分")
        else:
            # 尝试按品质出售
            price = await sell_fish(event.user_id, quality_name=msg)
            if price:
                await sell.send(f"成功出售所有{msg}品质的鱼，获得{price}钓鱼积分")
            else:
                return await sell.finish("没有这个品质/名字的鱼")

        await add_balance(to_uuid(event.get_user_id()), price, "卖鱼", FISHING_POINT.id)
    except NoneBotException:
        raise
    except Exception as e:
        logger.warning(f"卖鱼失败: {e}")
        await sell.send("发生错误，卖鱼失败了")


@bag.handle()
async def handle_bag(bot: Bot, event: MessageEvent):
    data = await get_user_data_pyd(event.user_id)
    msg_list = [
        MessageSegment.text(f"{event.sender.nickname}({event.get_user_id()})的背包：")
    ]

    # 按品质分类鱼
    quality_dict = {}
    for fish in data.fishes:
        quality = fish.metadata.quality
        name = fish.metadata.name

        if quality not in quality_dict:
            quality_dict[quality] = {}

        if name not in quality_dict[quality]:
            quality_dict[quality][name] = {"count": 0, "length": 0}

        quality_dict[quality][name]["count"] += 1
        quality_dict[quality][name]["length"] += fish.length

    # 构建消息
    for quality in QualityEnum:
        quality_value = quality.value
        if quality_value in quality_dict:
            section = [f"==={quality}品质==="]
            for name, fish_data in quality_dict[quality_value].items():
                total_length = fish_data["length"]
                length_str = format_length(total_length)
                section.append(f"{name}：{fish_data['count']}条，总长度{length_str}")
            msg_list.append(MessageSegment.text("\n".join(section)))

    await send_forward_msg(
        bot, event, config_manager.config.bot_name, str(event.self_id), msg_list
    )


@fishing.handle()
async def handle_fishing(bot: Bot, event: MessageEvent):
    user_id = str(event.user_id)
    config = config_manager.config

    # 检查冷却
    if not watch_user[user_id].consume():
        return await fishing.finish("鱼竿过热了，休息一下吧......")

    await fishing.send("正在钓鱼......")
    async with get_session() as session:
        user_meta = await get_or_create_user_model(event.user_id, session)
        session.add(user_meta)
        if isinstance(user_meta.last_fishing_time, str):
            try:
                user_meta.last_fishing_time = datetime.fromisoformat(
                    user_meta.last_fishing_time
                )
            except ValueError:
                user_meta.last_fishing_time = datetime.now()
        logger.debug(
            f"用户 {user_id} 今日钓鱼次数: {user_meta.today_fishing_count!s}, 上次钓鱼时间: {user_meta.last_fishing_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if not is_same_day(
            int(datetime.now().timestamp()),
            int(user_meta.last_fishing_time.timestamp()),
        ):
            user_meta.today_fishing_count = 0
            await session.commit()
            await session.refresh(user_meta)

        # 检查上限
        if user_meta.today_fishing_count >= config.fishing.max_fishing_count:
            return await fishing.finish("今天你不能再钓更多的鱼了，明天再来吧～")

        # 更新钓鱼次数
        user_meta.today_fishing_count += 1
        user_meta.last_fishing_time = datetime.now()
        await session.commit()
        await session.refresh(user_meta)

        # 确保附魔等级不超过上限
        lucky_level = min(user_meta.lucky_of_the_sea, MAX_ENCHANT_LEVEL)
        multi_level = min(user_meta.multi_fish, MAX_ENCHANT_LEVEL)
        feeding_level = min(user_meta.feeding, MAX_ENCHANT_LEVEL)

        # 计算概率
        luck_factor = 1 - (
            sqrt(lucky_level / config.fishing.probability.lucky_sqrt)
            / config.fishing.probability.lucky_sub
        )  # 0.2 at level 40
        if (
            user_meta.today_fishing_count >= config.fishing.max_fishing_count * 0.8
            and lucky_level <= 25
        ):
            luck_factor *= min(
                0.75
                * (config.fishing.max_fishing_count / user_meta.today_fishing_count),
                0.8,
            )
        probability = max(
            random.randint(1, 9999) / 10000 * luck_factor, MIN_PROBABILITY
        )

        # 钓鱼
        fishes = [await perform_fishing(event, session, probability, feeding_level)]

        # 多重钓竿
        if random.randint(1, 100) <= multi_level * 5:  # 5% per level,20 级则100%
            extra_count = max(
                int(2 * sqrt(multi_level / config.fishing.probability.multi_fish_sub)),
                1,
            )

            fishes.extend(
                [
                    await perform_fishing(event, session, probability, feeding_level)
                    for _ in range(extra_count)
                ]
            )

        await session.commit()
        await refresh_progress(event.user_id, session)

    # 构建结果消息
    fish_details = []
    for fish in fishes:
        detail = (
            f"[{fish.metadata.quality}]{fish.metadata.name} "
            f"长度：{format_length(fish.length)}"
        )
        if fish.metadata.prompt:
            detail += f"\n{fish.metadata.prompt}"
        fish_details.append(detail)

    result_msg = MessageSegment.reply(event.message_id) + MessageSegment.text(
        "你钓到了：\n" + "\n".join(fish_details) + "\n已收进背包～",
    )

    await fishing.finish(result_msg)


@progress.handle()
async def handle_progress(bot: Bot, event: MessageEvent):
    async with get_session() as session:
        await refresh_progress(event.user_id, session)
        user_meta = await get_or_create_user_model(
            event.user_id,
            session,
        )
        session.add(user_meta)
        progress_data = await get_user_progress(event.user_id, session)
        msg_list = []
        for quality in QualityEnum:
            all_fish_count = len(
                (
                    await session.execute(
                        select(FishMeta).where(FishMeta.quality == quality)
                    )
                )
                .scalars()
                .all()
            )
            this_count = len(progress_data.get(quality, []))
            msg_list.append(
                f"\n{quality}品质收集进度：{this_count}/{all_fish_count} ({this_count / all_fish_count:.2%})"
            )
        await progress.finish(
            f"{event.sender.nickname}({event.get_user_id()})的钓鱼进度：\n"
            f"今日钓鱼次数：{user_meta.today_fishing_count}/{config_manager.config.fishing.max_fishing_count}\n收集进度："
            + "".join(msg_list)
        )
