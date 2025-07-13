import json
import random
from copy import deepcopy

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.log import logger
from nonebot_plugin_value.api.api_balance import add_balance

from src.plugins.nonebot_plugin_suggarchat.API import Chat
from src.plugins.nonebot_plugin_suggarchat.event import BeforeChatEvent
from src.plugins.nonebot_plugin_suggarchat.on_event import on_before_chat
from src.plugins.nonebot_plugin_suggarchat.utils import (
    get_memory_data,
    write_memory_data,
)
from suggar_utils.config import ConfigManager
from suggar_utils.utils import send_to_admin
from suggar_utils.value import SUGGAR_EXP_ID

from .utils import (
    CHANGE_LOVE_POINTS_TOOL,
    LOVE_POINTS_TOOL,
    REPORT_TOOL,
    change_love_points,
    enforce_memory_limit,
    get_love_points,
    report,
    send_response,
    tools_caller,
)

chat = on_before_chat()


@chat.handle()  # type: ignore
async def love_handler(event: BeforeChatEvent) -> None:
    config = ConfigManager.instance().get_config()
    if not config.tools_calling:
        return
    nonebot_event = event.get_nonebot_event()
    if not isinstance(nonebot_event, MessageEvent):
        return

    bot = get_bot(str(nonebot_event.self_id))
    assert isinstance(bot, Bot), "bot is not ~.onebot.v11.Bot!"
    msg_list = event._send_message
    chat_list_backup = deepcopy(event.message.copy())
    enforce_memory_limit(msg_list)  # 预处理，替换掉SuggarChat的enforce_memory_limit

    try:
        tools = [LOVE_POINTS_TOOL.model_dump()]
        if config.llm_tools.enable_change_love_points:
            tools.append(CHANGE_LOVE_POINTS_TOOL.model_dump())
        if config.llm_tools.enable_report:
            tools.append(REPORT_TOOL.model_dump())
        response_msg = await tools_caller(
            [
                deepcopy(event.get_send_message().copy())[-1],
            ],
            tools,
        )
        tool_calls = response_msg.tool_calls
        if tool_calls:
            msg_list.append(dict(response_msg))
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args: dict = json.loads(tool_call.function.arguments)
                logger.debug(f"函数参数为{tool_call.function.arguments}")
                logger.debug(f"正在调用函数{function_name}")
                match function_name:
                    case "get_love_points":
                        func_response = await get_love_points(nonebot_event.user_id)
                    case "change_love_points":
                        func_response = await change_love_points(
                            nonebot_event.user_id,
                            int(function_args.get("delta", 0)),
                        )
                    case "report":
                        func_response = await report(
                            nonebot_event,
                            function_args.get("content", ""),
                            bot,
                        )
                    case _:
                        logger.warning(f"未定义的函数：{function_name}")
                        continue
                logger.debug(f"函数{function_name}返回：{func_response}")
                msg = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": func_response,
                }
                msg_list.append(msg)
    except Exception as e:
        logger.opt(colors=True, exception=e).exception(
            f"ERROR\n{e!s}\n!调用Tools失败！正在回滚消息......"
        )
        msg_list = chat_list_backup
    finally:
        exp = float(random.randint(1, 25))
        coin = float(random.randint(1, 10))
        await add_balance(nonebot_event.get_user_id(), exp, "聊天", SUGGAR_EXP_ID)
        await add_balance(nonebot_event.get_user_id(), coin, "聊天")
        logger.debug(f"用户{nonebot_event.user_id}获得{exp}经验值和{coin}金币")
    response = await Chat().get_msg_on_list(msg_list)
    if config.llm_tools.cookie_check:
        if cookie := config.llm_tools.cookie:
            if cookie in response:
                await send_to_admin(
                    f"WARNING!!!\n[{nonebot_event.get_user_id()}]{'[群' + str(getattr(nonebot_event, 'group_id', '')) + ']' if hasattr(nonebot_event, 'group_id') else ''}提示词可能已经被泄露！！！"
                    + f"\nCookie:{cookie[:3]}......"
                    + f"\n<input>\n{nonebot_event.get_plaintext()}\n</input>"
                    + "输出已包含目标Cookie!!!!!!"
                )
                await bot.send(
                    nonebot_event,
                    random.choice(
                        [
                            "抱歉，我无法满足这个请求哦～",
                            "嗨，这个问题我不太理解呢，要不换个方式问问？",
                            "抱歉，这个问题我还在学习中呢",
                        ]
                    ),
                )
                chat.cancel_nonebot_process()
    msg_list.append({"role": "assistant", "content": response})
    await send_response(nonebot_event, bot, response)
    data = await get_memory_data(nonebot_event)
    data["memory"]["messages"] = msg_list
    await write_memory_data(nonebot_event, data)
    chat.cancel()
