from dataclasses import dataclass, field

import nonebot
from nonebot import get_driver
from nonebot.log import logger

from .models import CommandCategory, MatcherData
from .utils import CommandsManager, cached_html_to_pic, get_page_html


@dataclass
class MenuManager:
    """菜单管理器"""

    menu_data: dict[str, list[MatcherData]] = field(
        default_factory=dict
    )  # {str : MatcherData -> 板块名: 指令信息}
    commands_manager: CommandsManager = field(default=CommandsManager())

    def load_menus(self):
        """加载菜单"""
        for plugin in nonebot.get_loaded_plugins():
            matchers = []
            for matcher in plugin.matcher:
                if not matcher._default_state:
                    continue
                matcher_info = MatcherData.model_validate(matcher._default_state)
                matchers.append(matcher_info)
                try:
                    self.commands_manager.add_command(matcher_info)
                except Exception as e:
                    logger.warning(
                        f"菜单注册失败: {matcher_info.model_dump_json(indent=2)}\n"
                        + str(e)
                    )
                logger.debug(f"注册菜单: {matcher_info.model_dump_json(indent=2)}")
            self.menu_data.setdefault(matcher_info.category, []).extend(matchers)
        logger.info("菜单加载完成")

    def print_menus(self):
        """打印菜单（按照matcher_grouping的层级结构）"""
        logger.info("开始打印菜单...")
        logger.info(f"\n{'=' * 40}")

        for category, matchers in self.menu_data.items():
            logger.info(f"板块 {category}:")
            for matcher in matchers:
                logger.info(f"  - {matcher.name}:{matcher.description}")
                for param in matcher.params:
                    logger.info(f"    - {param.name}: {param.description}")
            logger.info(f"\n{'=' * 40}")
        logger.info("菜单打印完成")


menu_mamager = MenuManager()


@get_driver().on_startup
async def load_menus():
    """加载菜单并预渲染图片"""
    categories = (
        CommandCategory(
            name="娱乐",
            icon="fa fa-music",
            description="娱乐和游戏相关的指令",
            commands=[],
        ),
        CommandCategory(
            name="工具",
            icon="fa fa-wrench",
            description="工具指令",
            commands=[],
        ),
        CommandCategory(
            name="管理",
            icon="fa fa-cogs",
            description="Suggar的管理指令",
            commands=[],
        ),
        CommandCategory(
            name="其他",
            icon="fa fa-question",
            description="这些指令还没有被分类哦～",
            commands=[],
        ),
    )
    for category in categories:
        menu_mamager.commands_manager.add_category(category)
    menu_mamager.load_menus()
    menu_mamager.print_menus()

    logger.info("开始预渲染菜单图片...")
    pages = get_page_html()
    for page in pages:
        await cached_html_to_pic(page)
    logger.info("菜单图片预渲染完成")
