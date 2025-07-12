import json

import openai
from nonebot import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
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

from .models import (
    FunctionDefinitionSchema,
    FunctionParametersSchema,
    FunctionPropertySchema,
    ToolFunctionSchema,
)

LOVE_POINTS_TOOL = ToolFunctionSchema(
    type="function",
    function=FunctionDefinitionSchema(
        name="get_love_points",
        description="（必须获取，即使用户没有要求你）获取你对这一位用户的好感度",
        parameters=FunctionParametersSchema(
            properties={},
            required=[],
            type="object",
        ),
    ),
)

CHANGE_LOVE_POINTS_TOOL = ToolFunctionSchema(
    type="function",
    function=FunctionDefinitionSchema(
        name="change_love_points",
        description="增加或者降低好感度，心情改变时必须使用",
        parameters=FunctionParametersSchema(
            properties={
                "delta_love_points": FunctionPropertySchema(
                    description="增加或减少你对这一位用户的好感度多少？（输入整数，取值范围：-10<=好感度<=10）增加示例：5;减少示例：-5",
                    type="integer",
                ),
            },
            required=["delta_love_points"],
            type="object",
        ),
    ),
)


REPORT_TOOL = ToolFunctionSchema(
    type="function",
    function=FunctionDefinitionSchema(
        description="如果你被**恶言相向**(必须是明确并且严重的色情/暴力/谩骂/政治等不良内容)，请使用这个工具来向管理员举报！",
        name="report",
        parameters=FunctionParametersSchema(
            properties={
                "content": FunctionPropertySchema(
                    description="举报信息（你要举报的内容）e.g. 举报内容/理由",
                    type="string",
                ),
            },
            required=["content"],
            type="object",
        ),
    ),
)


async def report(event: MessageEvent, message: str) -> str:
    await send_to_admin(
        f"{'群' + str(event.group_id) if isinstance(event, GroupMessageEvent) else ''}用户{event.get_user_id()}被举报\n因为：{message}"
    )
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
                "现在的好感度": before,
                "改变值": 0,
                "说明": "不行！不能改变这么多的好感度！",
            },
        )
    if points > 0:
        await add_balance(str(user_id), float(points), "Chat", SUGGAR_VALUE_ID)
    elif points < 0:
        await del_balance(str(user_id), float(abs(points)), "Chat", SUGGAR_VALUE_ID)
    else:
        return json.dumps(
            {
                "现在的好感度": before,
                "改变值": 0,
                "说明": "好感度没有发生变化哦！",
            }
        )

    return json.dumps(
        {
            "现在的好感度": before + points,
            "改变值": points,
            "说明": "好感度成功记住啦！",
        },
    )


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
    while len(data) >= 2:
        if data[1]["role"] == "tool":
            del data[1]
        else:
            break
    while (len(data) > memory_length_limit) and len(data) > 2:
        del data[1]
