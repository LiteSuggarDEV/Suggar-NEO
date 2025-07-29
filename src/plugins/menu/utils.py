import base64
import hashlib
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Literal

from nonebot_plugin_htmlrender import html_to_pic, md_to_pic
from typing_extensions import Self

from suggar_utils.config import CONFIG_DIR

from .models import CommandCategory, MatcherData, ParamType

dir_path = Path(__file__).parent
template_dir = dir_path / "templates"
PAGE_DIR = CONFIG_DIR / "pages"
PAGE_DIR.mkdir(parents=True, exist_ok=True)
_md_cache: dict[str, str] = {}
_html_cache: dict[str, str] = {}
page_list: list[str] = []


class CommandsManager:
    _instance = None
    categories: ClassVar[dict[str, CommandCategory]] = {}

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_category(self, category: CommandCategory) -> None:
        self.categories[category.name] = category

    def add_command(self, command: MatcherData) -> None:
        if command.category not in self.categories:
            raise ValueError(f"Category {command.category} not found")
        self.categories[command.category].commands.append(command)

    def get_menu_data(self) -> list[CommandCategory]:
        return [value for value in self.categories.values() if value.commands]

    def get_category(self, name: str) -> CommandCategory:
        return self.categories[name]


def get_css_path(name: Literal["dark", "light", ""] = "") -> str:
    if datetime.now().hour < 7 or datetime.now().hour > 20 or name == "dark":
        return str(dir_path / "dark.css")
    else:
        return str(dir_path / "light.css")


def _hash_md(md: str) -> str:
    return hashlib.sha256(md.encode("utf-8")).hexdigest()


async def cached_html_to_pic(html: str) -> str:
    key = _hash_md(html)
    if key in _html_cache:
        return _html_cache[key]
    bas64_img = f"base64://{base64.b64encode(await html_to_pic(html, viewport={'width': 600, 'height': 10})).decode('utf-8')}"
    _html_cache[key] = bas64_img
    return bas64_img


async def cached_md_to_pic(md: str, css_path: str) -> str:
    key = _hash_md(md + css_path)
    if key in _md_cache:
        return _md_cache[key + css_path]

    # 渲染图片，得到 base64
    base64_img = f"base64://{base64.b64encode(await md_to_pic(md=md, css_path=css_path)).decode()}"

    _md_cache[key + css_path] = base64_img
    return base64_img


def generate_command_card(command: MatcherData) -> str:
    """生成单个指令卡片的HTML"""
    # 处理参数
    params_html = ""
    for param in command.params:
        param_type_indicator = "?" if param.param_type == ParamType.OPTIONAL else "!"
        params_html += f"""
        <div class="param">
            <div class="param-name">{param.name} {param_type_indicator}</div>
            <div class="param-desc">{param.description}</div>
        </div>
        """

    # 处理示例
    examples_html = ""
    if command.examples:
        examples_html = "<div style='margin-top: 15px;'><strong>📝 示例:</strong>"
        for example in command.examples:
            examples_html += f"<div class='usage-box'>{example}</div>"
        examples_html += "</div>"

    # 处理别名
    aliases_html = ""
    if command.aliases:
        aliases_text = ", ".join(command.aliases)
        aliases_html = f"<div class='param'><div class='param-name'>别名</div><div class='param-desc'>{aliases_text}</div></div>"
    ln = "\n"
    return f"""
    <div class="command-card">
        <div class="command-header">
            <div class="command-icon" style="background-color: {command.color};">
                <i class="{command.icon if command.icon else CommandsManager().get_category(command.category).icon}"></i>
            </div>
            <div class="command-name">{command.name}</div>
        </div>
        <div class="command-desc">
            {command.description}
        </div>
        <div class="usage-box">
            {command.usage.replace(ln, "<br>")}
        </div>
        {aliases_html}
        {params_html}
        {examples_html}
    </div>
    """


def generate_category_html(category: CommandCategory) -> str:
    """生成整个分类的HTML"""
    category_html = f"""
    <div class="category-title">
        <i class="{category.icon}"></i>
        <span>{category.name}</span>
    </div>
    <div class="command-container" id="{category.name.lower().replace(" ", "-")}-commands">
    """

    for command in category.commands:
        category_html += generate_command_card(command)

    category_html += "</div>"
    return category_html


def generate_categories_volumn(categories: list[CommandCategory]) -> str:
    full_str = ""
    for category in categories:
        full_str += f"""<div class="category-title"><i class="{category.icon}"></i><span>{category.name}</span></div>"""
    return full_str


def pages_generator(
    categories: list[CommandCategory],
) -> Generator[tuple[CommandCategory, str]]:
    """生成整个页面的指令部分HTML"""
    for category in categories:
        yield category, generate_category_html(category)


def format_template(template: str, **kwargs: str) -> str:
    for k, v in kwargs.items():
        template = template.replace("{{" + k + "}}", v)
    return template


def get_page_html() -> list[str]:
    global page_list
    base_js = open(str(template_dir / "other.js"), encoding="utf-8").read()
    menu_data = CommandsManager().get_menu_data()
    page_list = [
        format_template(
            open(str(template_dir / "template.html"), encoding="utf-8").read(),
            script=base_js
            + (
                f"\ndocument.getElementById('command-categories').innerHTML = `{generate_categories_volumn(menu_data)}`;"
            ),
        )
    ]
    for category, page in pages_generator(menu_data):
        content = format_template(
            open(str(template_dir / "command.html"), encoding="utf-8").read(),
            script=base_js
            + (
                f"\ndocument.getElementById('command-categories').innerHTML = `{page}`;"
            ),
            category=category.name,
        )
        page_list.append(content)
    return page_list
