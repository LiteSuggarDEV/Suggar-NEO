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

from suggar_utils.value import SUGGAR_VALUE_ID


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
                "message": "好感度输入的数值过大啦！记不住啦！",
            },
        )

    if points > 0:
        await add_balance(str(user_id), points, "Chat", SUGGAR_VALUE_ID)
    else:
        await del_balance(str(user_id), points, "Chat", SUGGAR_VALUE_ID)
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
            "name": "change_love_points",
            "description": "描述：添加或减少你对这一位用户的好感度",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta_love_points": {
                        "type": "integer",
                        "description": "添加或者减少你对这一位用户的好感度（整数，取值范围：-10~10）",
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
