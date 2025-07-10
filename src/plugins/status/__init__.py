from nonebot.plugin import PluginMetadata, require

require("menu")
from . import status

__plugin_meta__ = PluginMetadata(
    name="状态插件",
    description="获取状态信息",
    usage="/status",
    type="application",
)
__all__ = [
    "status",
]
