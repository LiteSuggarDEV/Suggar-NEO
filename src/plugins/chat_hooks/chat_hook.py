import json
import random
from copy import deepcopy

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.log import logger
from nonebot_plugin_suggarchat.event import BeforeChatEvent
from nonebot_plugin_suggarchat.on_event import on_before_chat
from nonebot_plugin_value.api.api_balance import add_balance

from suggar_utils.config import ConfigManager
from suggar_utils.value import SUGGAR_EXP_ID

from .utils import (
    TOOLS,
    add_love_points,
    decrease_love_points,
    get_love_points,
    report,
    tools_caller,
)

chat = on_before_chat()


@chat.handle()  # type: ignore
async def love_handler(event: BeforeChatEvent) -> None:
    if not ConfigManager.instance().get_config().tools_calling:
        return
    nonebot_event = event.get_nonebot_event()
    if not isinstance(nonebot_event, MessageEvent):
        return
    msg_chat_list: list[dict] = event.message
    chat_list_backup = deepcopy(msg_chat_list)
    try:
        response_msg = await tools_caller(
            [deepcopy(msg_chat_list[0]), deepcopy(event.get_send_message().copy())[-1]],
            TOOLS,
        )
        tool_calls = response_msg.tool_calls
        if tool_calls:
            msg_chat_list.append(dict(response_msg))
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args: dict = json.loads(tool_call.function.arguments)
                match function_name:
                    case "get_love_points":
                        func_response = await get_love_points(nonebot_event.user_id)
                    case "add_love_points":
                        func_response = await add_love_points(
                            nonebot_event.user_id,
                            function_args.get("delta_love_points", 0),
                        )
                    case "decrease_love_points":
                        func_response = await decrease_love_points(
                            nonebot_event.user_id,
                            function_args.get("delta_love_points", 0),
                        )
                    case "report":
                        func_response = await report(
                            nonebot_event.user_id,
                            function_args.get("content", ""),
                        )
                msg_chat_list.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": func_response,
                    }
                )
    except Exception as e:
        logger.exception(f"ERROR{e!s}!调用Tools失败！正在回滚消息......")
        msg_chat_list = chat_list_backup
    finally:
        exp = random.randint(1, 25)
        coin = random.randint(1, 10)
        await add_balance(str(nonebot_event.user_id), exp, "聊天", SUGGAR_EXP_ID)
        await add_balance(str(nonebot_event.user_id), coin, "聊天")
        logger.debug(f"用户{nonebot_event.user_id}获得{exp}经验值和{coin}金币")
