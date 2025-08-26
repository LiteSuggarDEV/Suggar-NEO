import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiofiles
import yaml
from nonebot import logger
from pydantic import BaseModel
from typing_extensions import Self
from watchfiles import awatch

from .store import CONFIG_DIR


class ProbabilityFactor(BaseModel):
    """
    Set a probability factor for fishing.

    The probability factor is calculated as follows:
    lucky_factor -> f(lucky_level) = sqrt(lucky_level / lucky_sqrt) / lucky_sub
    probability = lucky_factor * random.random() if it's bigger than 0.01 else it will be 0.01. (random.random() in [0, 1])
    We will choose a fish quality which is not bigger than the probability, then choose a fish from the quality randomly.
    """

    lucky_sqrt: int = 6
    lucky_sub: int = 6
    # If user has muilti fish buff, fish_count = max(1, 2 * sqrt(multi_fish_level / multi_fish_sub))
    multi_fish_sub: int = 3


class FishingConfig(BaseModel):
    rate_limit: int = 6
    max_fishing_count: int = 60
    probability: ProbabilityFactor = ProbabilityFactor()
    eco2fishing: bool = False  # 在这一次启动中会把账户所有余额转换为钓鱼积分


class Config(BaseModel):
    fishing: FishingConfig = FishingConfig()
    reset_balance: bool = (
        False  # 在这一次启动中会按比例重置所有用户的余额（解决通货膨胀）
    )


class ConfigManager:
    config_path: Path = CONFIG_DIR / "config.yaml"
    _config: Config = Config()
    _lock: asyncio.Lock
    _task: asyncio.Task
    _instance = None
    _initialized: bool = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not getattr(self, "_initialized", False):
            self._config = Config()
            self._lock = asyncio.Lock()
            self._load_config_sync()
            self._initialized = True

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
