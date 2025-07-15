import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiofiles
import yaml
from nonebot import logger
from pydantic import BaseModel
from watchfiles import awatch

from .store import CONFIG_DIR


class LLM_Extension(BaseModel):
    enable_auto_switch: bool = True
    avaliable_presets: list[str] = ["default"]  # 自动切换可用模型的列表


class LLMTools(BaseModel):
    enable_report: bool = True
    require_tools: bool = False


class Cookie(BaseModel):
    cookie_check: bool = False
    cookie: str = ""
    block_msg: list[str] = [
        "喵呜～这个问题有点超出Suggar的理解范围啦(歪头)",
        "（耳朵耷拉）这个...Suggar暂时回答不了呢＞﹏＜",
        "喵？这个话题好像不太适合讨论呢～",
        "（玩手指）突然有点不知道该怎么回答喵...",
        "唔...这个方向Suggar还没学会呢(脸红)",
        "喵～我们聊点别的开心事好不好？",
        "（眨眨眼）这个话题好像被魔法封印了喵！",
        "啊啦～Suggar的知识库这里刚好是空白页呢",
        "（竖起尾巴）检测到未知领域警报喵！",
        "喵呜...这个问题让Suggar的CPU过热啦(＞﹏＜)",
        "（躲到主人身后）这个...好难回答喵...",
        "叮！话题转换卡生效～我们聊点别的喵？",
        "（猫耳抖动）信号接收不良喵...换个频道好吗？",
        "Suggar的喵星语翻译器好像故障了...",
        "（转圈圈）这个问题转晕Suggar啦～",
        "喵？刚才风太大没听清...主人再说点别的？",
        "（翻书状）Suggar的百科全书缺了这一页喵...",
        "啊呀～这个话题被猫毛盖住了看不见喵！",
        "（举起爪子投降）这个领域Suggar认输喵～",
        "检测到话题黑洞...紧急逃离喵！(＞人＜)",
        "（尾巴打结）这个问题好复杂喵...解不开啦",
        "喵呜～Suggar的小脑袋暂时处理不了这个呢",
        "（捂耳朵）不听不听～换话题喵！",
        "这个...Suggar的猫娘执照没覆盖这个领域喵",
        "叮咚！您的话题已进入Suggar的认知盲区～",
        "（装傻）喵？Suggar突然失忆了...",
        "警报！话题超出Suggar的可爱范围～",
        "（数爪子）1、2、3...啊数错了！换个话题喵？",
        "这个方向...Suggar的导航仪失灵了喵(´･_･`)",
        "喵～话题防火墙启动！我们聊点安全的？",
        "（转笔状）这个问题...考试不考喵！跳过～",
        "啊啦～Suggar的答案库正在升级中...",
        "（做鬼脸）略略略～不回答这个喵！",
        "检测到超纲内容...启动保护模式喵！",
        "（抱头蹲防）问题太难了喵！投降～",
        "喵呜...这个秘密要等Suggar升级才能解锁",
        "（举白旗）这个话题Suggar放弃思考～",
        "叮！触发Suggar的防宕机保护机制喵",
        "（装睡）Zzz...突然好困喵...",
        "喵？Suggar的思维天线接收不良...",
        "（画圈圈）这个问题在Suggar的知识圈外...",
        "啊呀～话题偏离主轨道喵！紧急修正～",
        "（翻跟头）问题太难度把Suggar绊倒了喵！",
        "这个...需要猫娘高级权限才能解锁喵～",
        "（擦汗）Suggar的处理器过载了...",
        "喵呜～问题太深奥会卡住Suggar的猫脑",
        "（变魔术状）看！话题消失魔术成功喵～",
    ]


class Config(BaseModel):
    tools_calling: bool = True
    rate_limit: int = 3
    notify_group: list[int] = [
        1002495699,
    ]
    admins: list[int] = [
        3196373166,
    ]
    llm_extension: LLM_Extension = LLM_Extension()
    llm_tools: LLMTools = LLMTools()
    cookies: Cookie = Cookie()


class ConfigManager:
    config_path: Path = CONFIG_DIR / "config.yaml"
    _config: Config = Config()
    _task: asyncio.Task
    _sug_task: asyncio.Task

    def __init__(self) -> None:
        self._config = Config()
        self._lock = asyncio.Lock()
        self._load_config_sync()

    def init_watch(self):
        self._task = asyncio.create_task(self._watch_config())

    def _load_config_sync(self) -> None:
        logger.info(f"正在加载配置文件: {self.config_path}")
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as f:
                self._config = Config.model_validate(yaml.safe_load(f) or {})
        self._save_config_sync()

    def _save_config_sync(self, path: Path | None = None) -> None:
        if not path:
            path = self.config_path
        with path.open("w", encoding="utf-8") as f:
            f.write(
                yaml.safe_dump(
                    self._config.model_dump(),
                    allow_unicode=True,
                )
            )

    async def _watch_files(
        self, paths: Path, refresh_func: Callable[..., Awaitable[Any]]
    ):
        async for changes in awatch(paths):
            if any(path == str(paths) for _, path in changes):
                logger.info("检测到配置文件变更，正在自动重载...")
                try:
                    await refresh_func()
                except Exception as e:
                    logger.opt(exception=e).warning("配置文件重载失败")

    async def _watch_config(self) -> None:
        await self._watch_files(self.config_path, self.reload_config)

    async def reload_config(self) -> Config:
        async with self._lock:
            if not self.config_path.exists():
                await self.save_config()
            else:
                async with aiofiles.open(self.config_path, encoding="utf-8") as f:
                    content = await f.read()
                self._config = Config.model_validate(yaml.safe_load(content) or {})
        logger.info("配置文件已重新加载")
        return self._config

    async def save_config(self) -> None:
        async with self._lock:
            data = yaml.safe_dump(self._config.model_dump(), allow_unicode=True)
            async with aiofiles.open(self.config_path, "w", encoding="utf-8") as f:
                await f.write(data)

    async def override_config(self, config: Config) -> None:
        safe_old = self._safe_dump(self._config)
        safe_new = self._safe_dump(config)
        logger.warning(
            "正在覆写配置文件!\n原始值:\n%s\n修改后:\n%s", safe_old, safe_new
        )

        async with self._lock:
            self._config = Config.model_validate(config)
            await self.save_config()

    def get_config(self) -> Config:
        return self._config

    @property
    def config(self) -> Config:
        return self._config

    @staticmethod
    def _safe_dump(config: Config) -> str:
        config_dict = config.model_dump()
        if "admins" in config_dict:
            config_dict["admins"] = ["***"]
        return yaml.safe_dump(config_dict, allow_unicode=True)


config_manager = ConfigManager()
