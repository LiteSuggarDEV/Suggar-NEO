from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class QualityMeta(BaseModel):
    name: str
    probability: float
    price_per_length: float
    length_range_start: int
    length_range_end: int


class FishMeta(BaseModel):
    name: str  # 名称
    quality: str
    quality_data: QualityMeta | None = None
    prompt: str = ""


class Fish(BaseModel):
    user_id: str
    length: int
    time: datetime
    metadata: FishMeta


class UserData(BaseModel):
    user_id: int
    fishes: list[Fish]


class QualityEnum(str, Enum):
    UNKNOWN = "???"
    SUPER_RARE = "神秘"
    LEGENDARY = "传说"
    MYTHICAL = "神话"
    EPIC = "史诗"
    RARE = "稀有"
    GOOD = "上等"
    COMMON = "普通"
    BAD = "腐烂"


DEFAULT_QUALITY = [
    QualityMeta(
        name=QualityEnum.BAD,
        probability=0.25,
        price_per_length=5.0,
        length_range_start=5,
        length_range_end=5,
    ),
    QualityMeta(
        name=QualityEnum.COMMON,
        probability=0.6,
        price_per_length=1.0,
        length_range_start=15,
        length_range_end=35,
    ),
    QualityMeta(
        name=QualityEnum.GOOD,
        probability=0.3,
        price_per_length=2.0,
        length_range_start=30,
        length_range_end=100,
    ),
    QualityMeta(
        name=QualityEnum.RARE,
        probability=0.1,
        price_per_length=5.0,
        length_range_start=1000,
        length_range_end=5000,
    ),
    QualityMeta(
        name=QualityEnum.EPIC,
        probability=0.05,
        price_per_length=10.0,
        length_range_start=5000,
        length_range_end=10000,
    ),
    QualityMeta(
        name=QualityEnum.LEGENDARY,
        probability=0.03,
        price_per_length=20.0,
        length_range_start=10000,
        length_range_end=50000,
    ),
    QualityMeta(
        name=QualityEnum.MYTHICAL,
        probability=0.02,
        price_per_length=30.0,
        length_range_start=25000,
        length_range_end=65000,
    ),
    QualityMeta(
        name=QualityEnum.SUPER_RARE,
        probability=0.015,
        price_per_length=40.0,
        length_range_start=65000,
        length_range_end=200000,
    ),
    QualityMeta(
        name=QualityEnum.UNKNOWN,
        probability=0.01,
        price_per_length=0,
        length_range_start=11451419,
        length_range_end=11451419,
    ),
]

DEFAULT_FISH_LIST = [
    # 腐烂品质
    FishMeta(
        name="腐烂的沙丁鱼",
        quality=QualityEnum.BAD,
    ),
    FishMeta(
        name="过期带鱼",
        quality=QualityEnum.BAD,
    ),
    FishMeta(
        name="学计算机的鱼",
        quality=QualityEnum.BAD,
        prompt="还是Jvav大蛇",
    ),
    FishMeta(
        name="程序员罗非鱼",
        quality=QualityEnum.BAD,
        prompt="聪明绝顶 不毛之地",
    ),
    # 普通品质
    FishMeta(
        name="鲤鱼",
        quality=QualityEnum.COMMON,
    ),
    FishMeta(
        name="草鱼",
        quality=QualityEnum.COMMON,
    ),
    FishMeta(
        name="鲫鱼",
        quality=QualityEnum.COMMON,
    ),
    FishMeta(
        name="鲢鱼",
        quality=QualityEnum.COMMON,
    ),
    FishMeta(
        name="摸鱼",
        quality=QualityEnum.COMMON,
    ),
    FishMeta(
        name="单身狗鱼",
        quality=QualityEnum.COMMON,
    ),
    # 上等品质
    FishMeta(
        name="鲈鱼",
        quality=QualityEnum.GOOD,
    ),
    FishMeta(
        name="鳜鱼",
        quality=QualityEnum.GOOD,
    ),
    FishMeta(
        name="三文鱼",
        quality=QualityEnum.GOOD,
    ),
    FishMeta(
        name="凡尔赛金鱼",
        quality=QualityEnum.GOOD,
    ),
    FishMeta(
        name="锦鲤",
        quality=QualityEnum.GOOD,
    ),
    # 稀有品质
    FishMeta(
        name="金龙鱼",
        quality=QualityEnum.RARE,
    ),
    FishMeta(
        name="孔雀鱼",
        quality=QualityEnum.RARE,
    ),
    FishMeta(
        name="996福报鱼",
        quality=QualityEnum.RARE,
    ),
    FishMeta(
        name="键盘侠鱼",
        quality=QualityEnum.RARE,
    ),
    # 史诗品质
    FishMeta(
        name="坤坤鱼",
        quality=QualityEnum.EPIC,
        prompt="可惜不会唱跳RAP篮球了",
    ),
    FishMeta(
        name="中华鲟",
        quality=QualityEnum.EPIC,
    ),
    FishMeta(
        name="蓝鳍金枪鱼",
        quality=QualityEnum.EPIC,
    ),
    FishMeta(
        name="鲲鹏幼体",
        quality=QualityEnum.EPIC,
    ),
    FishMeta(
        name="利维坦幼崽",
        quality=QualityEnum.EPIC,
    ),
    # 传说品质
    FishMeta(
        name="黄唇鱼",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="儒艮",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="阴阳鱼",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="达拉然魔法鱼",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="京鱼",
        quality=QualityEnum.LEGENDARY,
        prompt="AUV您吉祥",
    ),
    # 神话品质
    FishMeta(
        name="鲛人",
        quality=QualityEnum.MYTHICAL,
    ),
    FishMeta(
        name="禺强之鱼",
        quality=QualityEnum.MYTHICAL,
    ),
    FishMeta(
        name="亚特兰蒂斯守卫",
        quality=QualityEnum.MYTHICAL,
    ),
    FishMeta(
        name="NFT鱼",
        quality=QualityEnum.MYTHICAL,
    ),
    # 神秘品质
    FishMeta(
        name="克苏鲁幼体",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="时空穿梭鱼",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="薛定谔的鱼",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="戴森球能量鱼",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="深海巨怪克拉肯",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="横公鱼",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="鰼鰼鱼",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="鱼虎",
        quality=QualityEnum.EPIC,
    ),
    FishMeta(
        name="太极阴阳鱼·小柒",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="太极阴阳鱼·小叁",
        quality=QualityEnum.LEGENDARY,
    ),
    FishMeta(
        name="程序员咸鱼",
        quality=QualityEnum.RARE,
    ),
    FishMeta(
        name="忧伤水滴鱼",
        quality=QualityEnum.SUPER_RARE,
    ),
    FishMeta(
        name="防火鬼鮋",
        quality=QualityEnum.EPIC,
    ),
    # ?
    FishMeta(
        name="那一天的鱿鱼",
        quality=QualityEnum.UNKNOWN,
        prompt="啥 啊 这 是",
    ),
    FishMeta(
        name="东北鱼姐",
        quality=QualityEnum.UNKNOWN,
        prompt="带派的鱼",
    ),
    FishMeta(
        name="萨卡班甲鱼",
        quality=QualityEnum.RARE,
        prompt="萨卡班甲鱼～",
    ),
    FishMeta(
        name="玉！",
        quality=QualityEnum.UNKNOWN,
        prompt="合乎粥礼的鱼",
    ),
    FishMeta(
        name="河",
        quality=QualityEnum.SUPER_RARE,
        prompt="?你钓到了一条河？！",
    ),
    FishMeta(
        name="JohnRichard",
        quality=QualityEnum.UNKNOWN,
        prompt="这是谁",
    ),
    FishMeta(
        name="Mrling",
        quality=QualityEnum.UNKNOWN,
        prompt="这是串场了嘛",
    ),
]
