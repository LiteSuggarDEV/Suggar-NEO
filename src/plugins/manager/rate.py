import contextlib
import random
from collections import defaultdict

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
)
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import CommandArg
from nonebot.rule import (
    CommandRule,
    EndswithRule,
    FullmatchRule,
    KeywordsRule,
    RegexRule,
    ShellCommandRule,
    StartswithRule,
    ToMeRule,
)

from suggar_utils.config import config_manager
from suggar_utils.dump_tools import StatusManager
from suggar_utils.rule import is_global_admin
from suggar_utils.token_bucket import TokenBucket

watch_group = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.rate_limit, capacity=1)
)
watch_user = defaultdict(
    lambda: TokenBucket(rate=1 / config_manager.config.rate_limit, capacity=1)
)


@on_command("set_enable", priority=2).handle()
async def _(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if not await is_global_admin(event):
        return
    arg = args.extract_plain_text().strip()
    if arg in ("true", "yes", "1", "on"):
        StatusManager().set_disable(False)
        await matcher.finish("已启用")
    elif arg in ("false", "no", "0", "off"):
        StatusManager().set_disable(True)
        await matcher.finish("已关闭")
    else:
        await matcher.finish("请输入正确的参数，true/yes/1/on/false/no/0/off")


@run_preprocessor
async def poke(matcher: Matcher, event: PokeNotifyEvent):
    if event.target_id != event.self_id:
        return
    ins_id = str(event.group_id if event.group_id else event.user_id)
    data = watch_group if event.group_id else watch_user

    bucket = data[ins_id]
    if not bucket.consume():
        raise IgnoredException("Rate limit exceeded, operation ignored.")
    if (not StatusManager().ready) and (not await is_global_admin(event)):
        with contextlib.suppress(Exception):
            await matcher.send("正在维护/数据迁移中，暂时不支持该操作！")
        raise IgnoredException("Maintenance in progress, operation not supported.")


@run_preprocessor
async def run(matcher: Matcher, event: MessageEvent):
    has_text_rule = any(
        isinstance(
            checker.call,
            FullmatchRule
            | CommandRule
            | StartswithRule
            | EndswithRule
            | KeywordsRule
            | ShellCommandRule
            | RegexRule
            | ToMeRule,
        )
        for checker in matcher.rule.checkers
    )  # 检查该匹配器是否有文字类匹配类规则

    ins_id = str(
        event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
    )
    data = watch_group if isinstance(event, GroupMessageEvent) else watch_user

    bucket = data[ins_id]
    if not bucket.consume():
        if has_text_rule:
            with contextlib.suppress(Exception):
                await matcher.send(random.choice(config_manager.config.rate_reply))
        raise IgnoredException("Rate limit exceeded, operation ignored.")
    if (not StatusManager().ready) and (not await is_global_admin(event)):
        if has_text_rule:
            with contextlib.suppress(Exception):
                await matcher.send("正在维护/数据迁移中，暂时不支持该操作！")
        raise IgnoredException("Maintenance in progress, operation not supported.")
