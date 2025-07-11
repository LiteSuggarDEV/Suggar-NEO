import json

import openai
from nonebot import logger
from nonebot_plugin_suggarchat.API import config_manager
from nonebot_plugin_suggarchat.utils import ChatCompletion
from nonebot_plugin_value.api.api_balance import (
    add_balance,
    del_balance,
    get_or_create_account,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from suggar_utils.utils import send_to_admin
from suggar_utils.value import SUGGAR_VALUE_ID


async def report(uid: int, message: str) -> str:
    await send_to_admin(f"用户{uid}被LLM指控\n{message}")
    return "已向ADMIN举报！"


async def get_love_points(uid: int) -> str:
    user = await get_or_create_account(str(uid), SUGGAR_VALUE_ID)
    logger.debug(f"调用了tool，{uid}好感度为：{user.balance}")
    return json.dumps(
        {
            "now_love_points": user.balance,
        },
    )


async def change_love_points(user_id: int | str, points: int) -> str:
    before = (await get_or_create_account(str(user_id), SUGGAR_VALUE_ID)).balance
    logger.debug(f"调起了tool，尝试把{user_id}的好感度做{points}的变化！")
    if abs(points) > 10:
        return json.dumps(
            {
                "now_love_points": before,
                "change_points": 0,
                "message": "不行！不能改变这么多的好感度！",
            },
        )
    if points > 0:
        await add_balance(str(user_id), float(points), "Chat", SUGGAR_VALUE_ID)
    elif points < 0:
        await del_balance(str(user_id), float(abs(points)), "Chat", SUGGAR_VALUE_ID)
    else:
        return json.dumps(
            {
                "now_love_points": before,
                "change_points": 0,
                "message": "好感度没有发生变化哦！",
            }
        )

    return json.dumps(
        {
            "now_love_points": before + points,
            "change_points": points,
            "message": "好感度成功记住啦！",
        },
    )


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "report",
            "description": "如果你被**恶言相向**(必须是明确并且严重的色情/暴力/谩骂/政治等不良内容)，请使用这个工具来向管理员举报！",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "求助信息（请包含用户ID，昵称，你要举报的内容）e.g. 12345678 <昵称> <举报内容/理由>",
                    },
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "change_love_points",
            "description": "随着你的好感度变化时**立即**调用。该用于增加或降低你对这一位用户的好感度",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta_love_points": {
                        "type": "integer",
                        "description": "增加或减少你对这一位用户的好感度多少？（输入整数，取值范围：-10<=好感度<=10）示例1：5;示例2：-5",
                    }
                },
                "required": ["delta_love_points"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_love_points",
            "description": "（必须获取，即使用户没有要求你）获取你对这一位用户的好感度",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


async def tools_caller(
    messages: list,
    tools: list,
) -> ChatCompletionMessage:
    config = config_manager.config
    preset = config_manager.get_preset(config.preset, fix=True, cache=False)

    base_url = preset.base_url
    key = preset.api_key
    model = preset.model

    logger.debug(f"开始获取 {preset.model} 的带有工具的对话")
    logger.debug(f"预设：{config_manager.config.preset}")
    logger.debug(f"密钥：{preset.api_key[:7]}...")
    logger.debug(f"协议：{preset.protocol}")
    logger.debug(f"API地址：{preset.base_url}")
    client = openai.AsyncOpenAI(
        base_url=base_url, api_key=key, timeout=config.llm_timeout
    )
    completion: ChatCompletion = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
        tool_choice="required",
        tools=tools,
    )
    return completion.choices[0].message


def enforce_memory_limit(data: list):
    """
    控制记忆长度，删除超出限制的旧消息，移除不支持的消息。
    """
    memory_length_limit = config_manager.config.memory_lenth_limit
    is_multimodal = config_manager.get_preset(config_manager.config.preset, fix=True)
    # Process multimodal messages when needed
    for message in data:
        if (
            isinstance(message["content"], dict)
            and not is_multimodal
            and message["role"] == "user"
        ):
            message_text = ""
            for content_part in message["content"]:
                if content_part["type"] == "text":
                    message_text += content_part["text"]
            message["content"] = message_text

    # Enforce memory length limit
    while len(data) >= 1:
        if data[1]["role"] == "tool":
            del data[1]
        else:
            break
    while (len(data) > memory_length_limit) and len(data) > 1:
        del data[1]
