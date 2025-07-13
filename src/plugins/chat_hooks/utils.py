import asyncio
import json
import random

import openai
from nonebot import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
    MessageSegment,
)
from nonebot_plugin_value.api.api_balance import (
    add_balance,
    del_balance,
    get_or_create_account,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)

from src.plugins.nonebot_plugin_suggarchat.API import config_manager
from src.plugins.nonebot_plugin_suggarchat.utils import (
    ChatCompletion,
    split_message_into_chats,
)
from suggar_utils.config import config_manager as sug_config
from suggar_utils.utils import send_forward_msg_to_admin
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
        description="（必须获取，即使用户没有要求你）获取你对这一位用户的好感度，函数返回值示例为{'success':True,'message':'当前好感值：9'}，**返回值必须包含在回答中**",
        parameters=FunctionParametersSchema(
            properties={},
            required=[],
            type="object",
        ),
        strict=False,
    ),
)


CHANGE_LOVE_POINTS_TOOL = ToolFunctionSchema(
    type="function",
    function=FunctionDefinitionSchema(
        name="change_love_points",
        description="设置好感度，好感度改变时**必须使用**，函数返回值示例为{'success':True,'message':'现在的好感值为：9'}，返回的最终值**必须包含在回答中**",
        parameters=FunctionParametersSchema(
            properties={
                "delta": FunctionPropertySchema(
                    description="增加或减少你对这一位用户的好感度多少？（输入整数，取值范围：-10<=好感度<=10）增加示例：5;减少示例：-5",
                    type="integer",
                    enum=[*range(-10, 10)],
                ),
            },
            required=["delta"],
            type="object",
        ),
        strict=True,
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


async def report(event: MessageEvent, message: str, bot: Bot) -> str:
    logger.warning(f"{event.user_id} 被举报了 ：{message}")
    await send_forward_msg_to_admin(
        bot,
        "Suggar-REPORT",
        str(event.self_id),
        [
            MessageSegment.text(
                f"{'群' + str(event.group_id) if isinstance(event, GroupMessageEvent) else ''}用户{event.get_user_id()}被举报"
            ),
            MessageSegment.text("LLM原因总结：\n" + message),
            MessageSegment.text(f"原始消息：\n{event.message.extract_plain_text()}"),
        ],
    )
    return json.dumps({"success": True, "message": "举报成功！"})


async def get_love_points(uid: int) -> str:
    user = await get_or_create_account(str(uid), SUGGAR_VALUE_ID)
    logger.debug(f"调用了tool，{uid}好感度为：{user.balance}")
    return json.dumps(
        {"success": True, "message": f"当前好感度：{user.balance}"},
        ensure_ascii=False,
    )


async def change_love_points(user_id: int | str, points: int) -> str:
    before = (await get_or_create_account(str(user_id), SUGGAR_VALUE_ID)).balance
    logger.debug(f"调起了tool，尝试把{user_id}的好感度做{points}的变化！")
    if abs(points) > 10:
        return json.dumps(
            {"success": False, "message": "Too large change!"},
            ensure_ascii=False,
        )
    if points > 0:
        await add_balance(str(user_id), float(points), "Chat", SUGGAR_VALUE_ID)
    elif points < 0:
        await del_balance(str(user_id), float(abs(points)), "Chat", SUGGAR_VALUE_ID)
    else:
        return json.dumps(
            {"success": False, "message": "无变化，好感度改变值为0。"},
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "success": True,
            "message": f"现在的好感度值是：{int(before + points)}，{'添加' if points > 0 else '减少'}了{abs(points)}点",
        },
        ensure_ascii=False,
    )


async def tools_caller(
    messages: list,
    tools: list,
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None,
) -> ChatCompletionMessage:
    if not tool_choice:
        tool_choice = (
            "required" if sug_config.config.llm_tools.require_tools else "auto"
        )
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
        tool_choice=tool_choice,
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
    if is_multimodal.multimodal:
        for message in data:
            if isinstance(message["content"], dict) and message["role"] == "user":
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
    while len(data) > memory_length_limit:
        del data[1]


async def send_response(event: MessageEvent, bot: Bot, response: str):
    """
    发送聊天模型的回复，根据配置选择不同的发送方式。
    """
    if not config_manager.config.nature_chat_style:
        await bot.send(
            event,
            MessageSegment.reply(event.message_id) + MessageSegment.text(response),
        )
    elif response_list := split_message_into_chats(response):
        for message in response_list:
            await bot.send(event, MessageSegment.text(message))
            await asyncio.sleep(
                random.randint(1, 3) + (len(message) // random.randint(80, 100))
            )
