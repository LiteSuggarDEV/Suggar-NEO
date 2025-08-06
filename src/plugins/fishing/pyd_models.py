from datetime import datetime
from enum import Enum

from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData
from nonebot_plugin_value.uuid_lib import to_uuid
from pydantic import BaseModel

FISHING_POINT = CurrencyData(
    id=to_uuid(
        "fishing_point",
    ),
    allow_negative=False,
    display_name="钓鱼点数",
    default_balance=0,
    symbol="🎣",
)


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
        price_per_length=0.5,
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
        probability=0.07,
        price_per_length=5.0,
        length_range_start=100,
        length_range_end=500,
    ),
    QualityMeta(
        name=QualityEnum.EPIC,
        probability=0.03,
        price_per_length=8.0,
        length_range_start=500,
        length_range_end=2000,
    ),
    QualityMeta(
        name=QualityEnum.LEGENDARY,
        probability=0.02,
        price_per_length=10.0,
        length_range_start=2000,
        length_range_end=6000,
    ),
    QualityMeta(
        name=QualityEnum.MYTHICAL,
        probability=0.01,
        price_per_length=14.0,
        length_range_start=6000,
        length_range_end=20000,
    ),
    QualityMeta(
        name=QualityEnum.SUPER_RARE,
        probability=0.005,
        price_per_length=20.0,
        length_range_start=20000,
        length_range_end=50000,
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
    # 新增腐烂品质
    FishMeta(
        name="福岛变异鱼",
        quality=QualityEnum.BAD,
        prompt="自带荧光特效",
    ),
    FishMeta(
        name="钉钉打卡鱼", quality=QualityEnum.BAD, prompt="每日自动发送「已打卡」"
    ),
    # 新增普通品质
    FishMeta(
        name="P社玩家鱼",
        quality=QualityEnum.COMMON,
        prompt="会喊「刁民住口」",
    ),
    FishMeta(
        name="甲方需求鱼", quality=QualityEnum.COMMON, prompt="反复横跳的七彩渐变色"
    ),
    # 新增上等品质
    FishMeta(
        name="赛博朋克2077鱼",
        quality=QualityEnum.GOOD,
        prompt="内置未修复的BUG",
    ),
    # 新增稀有品质
    FishMeta(
        name="流浪地球MOSS鱼",
        quality=QualityEnum.RARE,
        prompt="不断重复「让人类保持理智是奢求」",
    ),
    FishMeta(
        name="戴森球计划矿鱼",
        quality=QualityEnum.RARE,
        prompt="体内含钛矿石",
    ),
    # 新增史诗品质
    FishMeta(
        name="艾泽拉斯鱼人", quality=QualityEnum.EPIC, prompt="会喊「呜啦啦啦啦」"
    ),
    FishMeta(
        name="三体脱水鱼",
        quality=QualityEnum.EPIC,
        prompt="遭遇危机自动变鱼干",
    ),
    # 新增传说品质
    FishMeta(
        name="宝可梦·鲤鱼王", quality=QualityEnum.LEGENDARY, prompt="只会水溅跃的神兽"
    ),
    FishMeta(
        name="西游记奔波儿灞",
        quality=QualityEnum.LEGENDARY,
        prompt="喊「爷爷饶命」的鲇鱼精",
    ),
    # 新增神话品质
    FishMeta(
        name="北欧世界之鱼", quality=QualityEnum.MYTHICAL, prompt="环绕尘世巨蟒的眷属"
    ),
    FishMeta(
        name="山海经·赢鱼",
        quality=QualityEnum.MYTHICAL,
        prompt="翼如鸟 鸣如磬",
    ),
    # 新增神秘品质
    FishMeta(
        name="MC方块鱼", quality=QualityEnum.SUPER_RARE, prompt="像素化外观 掉落经验球"
    ),
    FishMeta(
        name="SCP-5047鱼",
        quality=QualityEnum.SUPER_RARE,
        prompt="会背诵《出师表》的异常实体",
    ),
    # 新增未知品质
    FishMeta(
        name="咕咕咕鱼", quality=QualityEnum.UNKNOWN, prompt="程序员特供型 每月32日出现"
    ),
    FishMeta(
        name="二次元纸片鱼",
        quality=QualityEnum.UNKNOWN,
        prompt="没有厚度 无法被三维观测",
    ),
]
