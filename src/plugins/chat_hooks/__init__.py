from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_suggarchat")
require("nonebot_plugin_value")

from . import chat_hook

__all__ = [
    "chat_hook",
]

___plugin_meta__ = PluginMetadata(
    name="聊天",
    description="聊天辅助功能",
    usage="无",
    type="application",
    homepage="",
    supported_adapters={"~onebot.v11"},
)
