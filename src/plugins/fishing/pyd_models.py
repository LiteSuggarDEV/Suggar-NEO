from datetime import datetime

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


class Fish(BaseModel):
    user_id: str
    length: int
    time: datetime
    metadata: FishMeta


class UserData(BaseModel):
    user_id: int
    fishes: list[Fish]


DEFAULT_QUALITY = [
    QualityMeta(
        name="腐烂",
        probability=0.1,
        price_per_length=5.0,
        length_range_start=5,
        length_range_end=5,
    ),
    QualityMeta(
        name="普通",
        probability=0.4,
        price_per_length=1.0,
        length_range_start=15,
        length_range_end=35,
    ),
    QualityMeta(
        name="上等",
        probability=0.1,
        price_per_length=2.0,
        length_range_start=30,
        length_range_end=100,
    ),
    QualityMeta(
        name="稀有",
        probability=0.05,
        price_per_length=5.0,
        length_range_start=100,
        length_range_end=500,
    ),
    QualityMeta(
        name="史诗",
        probability=0.03,
        price_per_length=10.0,
        length_range_start=500,
        length_range_end=1000,
    ),
    QualityMeta(
        name="传说",
        probability=0.02,
        price_per_length=20.0,
        length_range_start=1000,
        length_range_end=5000,
    ),
    QualityMeta(
        name="神话",
        probability=0.02,
        price_per_length=30.0,
        length_range_start=2500,
        length_range_end=6500,
    ),
    QualityMeta(
        name="神秘",
        probability=0.015,
        price_per_length=40.0,
        length_range_start=6500,
        length_range_end=20000,
    ),
    QualityMeta(
        name="???",
        probability=0.01,
        price_per_length=0,
        length_range_start=114514,
        length_range_end=114514,
    ),
]

DEFAULT_FISH_LIST = [
    # 腐烂品质
    FishMeta(
        name="腐烂的沙丁鱼",
        quality="腐烂",
    ),
    FishMeta(
        name="过期带鱼",
        quality="腐烂",
    ),
    FishMeta(
        name="学计算机的鱼",
        quality="腐烂",
    ),
    FishMeta(
        name="程序员罗非鱼",
        quality="腐烂",
    ),
    # 普通品质
    FishMeta(
        name="鲤鱼",
        quality="普通",
    ),
    FishMeta(
        name="草鱼",
        quality="普通",
    ),
    FishMeta(
        name="鲫鱼",
        quality="普通",
    ),
    FishMeta(
        name="鲢鱼",
        quality="普通",
    ),
    FishMeta(
        name="摸鱼",
        quality="普通",
    ),
    FishMeta(
        name="单身狗鱼",
        quality="普通",
    ),
    # 上等品质
    FishMeta(
        name="鲈鱼",
        quality="上等",
    ),
    FishMeta(
        name="鳜鱼",
        quality="上等",
    ),
    FishMeta(
        name="三文鱼",
        quality="上等",
    ),
    FishMeta(
        name="凡尔赛金鱼",
        quality="上等",
    ),
    FishMeta(
        name="锦鲤",
        quality="上等",
    ),
    # 稀有品质
    FishMeta(
        name="金龙鱼",
        quality="稀有",
    ),
    FishMeta(
        name="孔雀鱼",
        quality="稀有",
    ),
    FishMeta(
        name="996福报鱼",
        quality="稀有",
    ),
    FishMeta(
        name="键盘侠鱼",
        quality="稀有",
    ),
    # 史诗品质
    FishMeta(
        name="中华鲟",
        quality="史诗",
    ),
    FishMeta(
        name="蓝鳍金枪鱼",
        quality="史诗",
    ),
    FishMeta(
        name="鲲鹏幼体",
        quality="史诗",
    ),
    FishMeta(
        name="利维坦幼崽",
        quality="史诗",
    ),
    # 传说品质
    FishMeta(
        name="黄唇鱼",
        quality="传说",
    ),
    FishMeta(
        name="儒艮",
        quality="传说",
    ),
    FishMeta(
        name="阴阳鱼",
        quality="传说",
    ),
    FishMeta(
        name="达拉然魔法鱼",
        quality="传说",
    ),
    # 神话品质
    FishMeta(
        name="鲛人",
        quality="神话",
    ),
    FishMeta(
        name="禺强之鱼",
        quality="神话",
    ),
    FishMeta(
        name="亚特兰蒂斯守卫",
        quality="神话",
    ),
    FishMeta(
        name="NFT鱼",
        quality="神话",
    ),
    # 神秘品质
    FishMeta(
        name="克苏鲁幼体",
        quality="神秘",
    ),
    FishMeta(
        name="时空穿梭鱼",
        quality="神秘",
    ),
    FishMeta(
        name="薛定谔的鱼",
        quality="神秘",
    ),
    FishMeta(
        name="戴森球能量鱼",
        quality="神秘",
    ),
    FishMeta(
        name="深海巨怪克拉肯",
        quality="神秘",
    ),
    FishMeta(
        name="横公鱼",
        quality="传说",
    ),
    FishMeta(
        name="鰼鰼鱼",
        quality="神秘",
    ),
    FishMeta(
        name="鱼虎",
        quality="史诗",
    ),
    FishMeta(
        name="太极阴阳鱼·小柒",
        quality="传说",
    ),
    FishMeta(
        name="太极阴阳鱼·小叁",
        quality="传说",
    ),
    FishMeta(
        name="程序员咸鱼",
        quality="腐烂",
    ),
    FishMeta(
        name="忧伤水滴鱼",
        quality="神秘",
    ),
    FishMeta(
        name="防火鬼鮋",
        quality="史诗",
    ),
    # ?
    FishMeta(
        name="那一天的鱿鱼",
        quality="???",
    ),
    FishMeta(
        name="东北鱼姐",
        quality="???",
    ),
    FishMeta(
        name="萨卡班甲鱼",
        quality="稀有",
    ),
]
