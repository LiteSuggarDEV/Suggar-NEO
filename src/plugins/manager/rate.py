import contextlib
import random
from collections import defaultdict

from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, PokeNotifyEvent
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.rule import (
    CommandRule,
    EndswithRule,
    FullmatchRule,
    KeywordsRule,
    RegexRule,
    ShellCommandRule,
    StartswithRule,
)

from suggar_utils.config import config_manager
from suggar_utils.dump_tools import MigrationManager
from suggar_utils.token_bucket import TokenBucket

watch_group = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.rate_limit, capacity=1)
)
watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.rate_limit, capacity=1)
)


@run_preprocessor
async def poke(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id != event.self_id:
        return
    ins_id = str(event.group_id if event.group_id else event.user_id)
    data = watch_group if event.group_id else watch_user

    bucket = data[ins_id]
    if not bucket.consume():
        raise IgnoredException("Too fast!")
    if MigrationManager().is_running():
        await matcher.send("正在维护/数据迁移中，暂时不支持该操作！")
        raise IgnoredException("Under repair/migration")


@run_preprocessor
async def run(matcher: Matcher, event: MessageEvent):
    if not any(
        isinstance(
            checker.call,
            FullmatchRule
            | CommandRule
            | StartswithRule
            | EndswithRule
            | KeywordsRule
            | ShellCommandRule
            | RegexRule,
        )
        for checker in matcher.rule.checkers
    ):  # 检查该匹配器是否有文字类匹配类规则
        return

    ins_id = str(
        event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
    )
    data = watch_group if isinstance(event, GroupMessageEvent) else watch_user

    bucket = data[ins_id]
    if not bucket.consume():
        with contextlib.suppress(Exception):
            await matcher.send(random.choice(config_manager.config.rate_reply))
        raise IgnoredException("Too fast!")
    if not MigrationManager().is_running():
        await matcher.send("正在维护/数据迁移中，暂时不支持该操作！")
        raise IgnoredException("Under repair/migration")
