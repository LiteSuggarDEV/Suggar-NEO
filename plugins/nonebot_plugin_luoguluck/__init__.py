from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_localstore")
require("menu")

from . import event, image

__all__ = [
    "event",
    "image",
]
__plugin_meta__ = PluginMetadata(
    name="LuoguLuck|洛谷运势",
    description="洛谷同款的今日运势插件！",
    usage="/luck",
    type="application",
    homepage="https://github.com/JohnRichard4096/luogu-luck",
    supported_adapters={"~onebot.v11"},
)
