from enum import Enum

import pydantic


class CategoryEnum(str, Enum):
    FUN = "娱乐"
    UTILS = "工具"
    MANAGE = "管理"
    UNKNOW = "其他"
    GAME = "游戏"


class ParamType(str, Enum):
    OPTIONAL = "optional"
    REQUIRED = "required"
    VARIADIC = "variadic"


class CommandParam(pydantic.BaseModel):
    name: str
    description: str
    param_type: ParamType = ParamType.OPTIONAL
    default: str | None = None


class MatcherData(pydantic.BaseModel):
    name: str
    description: str
    usage: str
    icon: str = ""
    color: str = "#ff9ed8"
    category: str = CategoryEnum.UNKNOW
    aliases: list[str] = []
    params: list[CommandParam] = []
    examples: list[str] = []


class CommandCategory(pydantic.BaseModel):
    name: str
    icon: str
    description: str
    commands: list[MatcherData] = []
