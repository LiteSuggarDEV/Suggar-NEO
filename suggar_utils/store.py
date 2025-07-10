import json

from nonebot import require
from pydantic import BaseModel, Field

require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_config_dir, get_data_dir

DATA_DIR = get_data_dir("suggar_original")
CONFIG_DIR = get_config_dir("suggar_original")

class UserData(BaseModel):
    daily_count: int = Field(default=0, description="签到次数")
    exp: int = Field(default=0, description="经验")
    last_daily: float = Field(default_factory=float, description="上次签到时间")
    bag: list = Field(default_factory=list, description="背包")




def save_fun_data(uid: str, data: UserData):
    data_path = DATA_DIR / f"{uid}.json"
    data_path.write_text(data.model_dump_json(indent=4), encoding="utf-8")


def get_fun_data(uid: str) -> UserData:
    data = UserData()
    data_path = DATA_DIR / f"{uid}.json"
    if not (data_path).exists():
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(dict(data), f)
    else:
        with open(data_path, encoding="utf-8") as f:
            data = UserData(**json.load(f))
    return data
