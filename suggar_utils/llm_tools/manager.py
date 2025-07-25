from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

from typing_extensions import Self

from .models import ToolData, ToolFunctionSchema


class ToolsManager:
    _instance = None
    __models: ClassVar[dict[str, ToolData]] = {}

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_tool(self, name: str, default: Any | None = None) -> ToolData | None | Any:
        return self.__models.get(name, default)

    def get_tool_meta(
        self, name: str, default: Any | None = None
    ) -> ToolFunctionSchema | None | Any:
        func_data = self.__models.get(name)
        if func_data is None:
            return default
        if isinstance(func_data, ToolData):
            return func_data.data
        return default

    def get_tool_func(
        self, name: str, default: Any | None = None
    ) -> Callable[[dict[str, Any]], Awaitable[str]] | None | Any:
        func_data = self.__models.get(name)
        if func_data is None:
            return default
        if isinstance(func_data, ToolData):
            return func_data.func
        return default

    def get_tools(self) -> dict[str, ToolData]:
        return self.__models

    def tools_meta(self) -> dict[str, ToolFunctionSchema]:
        return {k: v.data for k, v in self.__models.items()}

    def tools_meta_dict(self) -> dict[str, dict[str, Any]]:
        return {
            k: v.data.model_dump(exclude_none=True) for k, v in self.__models.items()
        }

    def register_tool(self, tool: ToolData) -> None:
        if tool.data.function.name not in self.__models:
            self.__models[tool.data.function.name] = tool

    def remove_tool(self, name: str) -> None:
        if name in self.__models:
            del self.__models[name]
