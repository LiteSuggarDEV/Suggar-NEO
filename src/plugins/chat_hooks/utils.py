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


async def decrease_love_points(user_id: int | str, points: int) -> str:
    before = (await get_or_create_account(str(user_id), SUGGAR_VALUE_ID)).balance
    logger.debug(f"调起了tool，尝试把{user_id}的好感度做{points}的变化！")
    if abs(points) > 10:
        return json.dumps(
            {
                "now_love_points": before,
                "change_points": 0,
                "message": "好感度输入的数值过小啦！记不住啦！",
            },
        )

    await del_balance(str(user_id), -abs(points), "Chat", SUGGAR_VALUE_ID)

    return json.dumps(
        {
            "now_love_points": before + points,
            "change_points": points,
            "message": "好感度成功记住啦！",
        },
    )


async def add_love_points(user_id: int | str, points: int) -> str:
    before = (await get_or_create_account(str(user_id), SUGGAR_VALUE_ID)).balance
    logger.debug(f"调起了tool，尝试把{user_id}的好感度做+{points}的变化！")
    if abs(points) > 10:
        return json.dumps(
            {
                "now_love_points": before,
                "change_points": 0,
                "message": "好感度输入的数值过大啦！记不住啦！",
            },
        )

    await add_balance(str(user_id), abs(points), "Chat", SUGGAR_VALUE_ID)

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
            "description": "如果你被**恶言相向**，请使用这个工具来向管理员举报！",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "求助信息（请包含用户ID，昵称，你要举报的内容）e.g. 12345678 QQ用户 <举报内容/理由>",
                    },
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "decrease_love_points",
            "description": "随着你的情绪变化时**立即**调用，且仅在好感度**降低**时必须调用。该工具降低你对这一位用户的好感度记录值",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta_love_points": {
                        "type": "integer",
                        "description": "减少你对这一位用户的好感度多少？（输入负整数，取值范围：-1~-10）",
                    }
                },
                "required": ["delta_love_points"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_love_points",
            "description": "随着你的情绪变化时**立即**调用，且仅在好感度**增加**时必须调用。该工具降低你对这一位用户的好感度记录值",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta_love_points": {
                        "type": "integer",
                        "description": "添加你对这一位用户的好感度多少？（输入正整数，取值范围：1~10）",
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
        tool_choice="auto",
        tools=tools,
    )
    return completion.choices[0].message
