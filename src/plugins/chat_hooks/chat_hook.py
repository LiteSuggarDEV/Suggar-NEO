import json
from copy import deepcopy

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.log import logger
from nonebot_plugin_suggarchat.event import BeforeChatEvent
from nonebot_plugin_suggarchat.on_event import on_before_chat

from suggar_utils.config import ConfigManager

from .utils import TOOLS, change_love_points, get_love_points, tools_caller

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
            [deepcopy(event.get_send_message().copy())[-1]], TOOLS
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
                    case "change_love_points":
                        func_response = await change_love_points(
                            nonebot_event.user_id,
                            function_args.get("delta_love_points", 0),
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
        logger.opt(exception=e).exception("ERROR!调用Tools失败！正在回滚消息......")
        msg_chat_list = chat_list_backup
