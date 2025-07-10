# -*- coding: utf-8 -*-
"""
@Author   : xy_cloud,JohnRichard4096
@IDE      : Visual Studio Code
@Project  : Python Project
@File     : image.py
"""

import base64
import io
import os
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def image_to_base64(image: Image) -> bytes: # type: ignore
    buffer = io.BytesIO()
    image.save(buffer, format="PNG") # type: ignore
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    img_bytes = base64.b64decode(img_str)
    return img_bytes


todolist = [
    ["刷B站", "承包一天笑点"],
    ["在QQ群聊天", "遇见好朋友"],
    ["被撅", "哼哼哼啊啊啊啊啊"],
    ["写作业", "蒙的全对"],
    ["唱跳RAP篮球", "只因你太美"],
    ["打游戏", "杀疯了"],
    ["摸鱼", "摸鱼不被发现"],
    ["玩原神", "抽卡全金"],
    ["玩mc", "进下界遇到远古残骸"],
    ["看电影", "找到一部超好看的电影"],
    ["学习新技能", "轻松掌握新知识"],
    ["做家务", "家里变得超级干净"],
    ["逛街", "买到喜欢的衣服"],
    ["做饭", "做出美味佳肴"],
    ["运动", "状态非常好"],
    ["阅读", "读到一本好书"],
    ["听音乐", "发现一首新歌"],
    ["购物", "买到物美价廉的东西"],
    ["散步", "心情舒畅"],
    ["画画", "画出满意的作品"],
    ["写作", "灵感涌现"],
    ["编程", "顺利解决难题"],
    ["学习外语", "进步明显"],
    ["做瑜伽", "身心放松"],
    ["摄影", "拍到美丽的风景"],
    ["烹饪", "尝试新菜谱成功"],
    ["看直播", "遇到有趣的主播"],
    ["聚会", "度过愉快的时光"],
    ["健身", "锻炼效果显著"],
    ["阅读新闻", "了解新资讯"],
    ["看纪录片", "增长见识"],
    ["练习乐器", "进步飞快"],
    ["打扫房间", "焕然一新"],
    ["做手工", "完成一件作品"],
    ["看电影", "感动落泪"],
    ["旅行", "体验不同的文化"],
    ["听讲座", "收获满满"],
    ["参加比赛", "获得好成绩"],
    ["看书", "学到新知识"],
    ["练字", "字体变漂亮"],
    ["写日记", "记录美好瞬间"],
    ["做甜品", "美味可口"],
    ["看动漫", "追完一季"],
    ["看小说", "一口气看完"],
    ["做PPT", "顺利完成"],
    ["练习舞蹈", "动作流畅"],
    ["做面膜", "皮肤变好"],
    ["刷oj", "全部accept"],
    ["刷题", "全部AC"],
    ["玩Linux", "[OK]"],
    ["上课", "全会了！"],
    ["考试", "考的全会"],
]
nottodolist = [
    ["刷B站", "视频加载不出来"],
    ["在QQ群聊天", "被小鬼气死"],
    ["被撅", "休息一天~"],
    ["写作业", "全错了"],
    ["唱跳RAP篮球", "被ikun人参公鸡"],
    ["打游戏", "送人头"],
    ["摸鱼", "摸鱼被发现"],
    ["玩原神", "抽卡九蓝一紫"],
    ["玩mc", "家被苦力怕炸"],
    ["看电影", "电影很无聊"],
    ["学习新技能", "学不会新知识"],
    ["做家务", "越做越乱"],
    ["逛街", "什么都没买到"],
    ["做饭", "糊锅了"],
    ["运动", "受伤了"],
    ["阅读", "看不进去书"],
    ["听音乐", "耳机坏了"],
    ["购物", "买到假货"],
    ["散步", "迷路了"],
    ["画画", "画得一团糟"],
    ["写作", "毫无灵感"],
    ["编程", "遇到奇怪的bug"],
    ["学习外语", "记不住单词"],
    ["做瑜伽", "拉伤肌肉"],
    ["摄影", "相机没电"],
    ["烹饪", "味道奇怪"],
    ["看直播", "网络卡顿"],
    ["聚会", "气氛尴尬"],
    ["健身", "肌肉酸痛"],
    ["阅读新闻", "全是负面消息"],
    ["看纪录片", "枯燥乏味"],
    ["练习乐器", "音准不准"],
    ["打扫房间", "灰尘满天"],
    ["做手工", "失败多次"],
    ["看电影", "剧情无聊"],
    ["旅行", "遇到恶劣天气"],
    ["听讲座", "听不懂"],
    ["参加比赛", "表现不佳"],
    ["看书", "看不懂"],
    ["练字", "字迹潦草"],
    ["写日记", "写不出东西"],
    ["做甜品", "烤焦了"],
    ["看动漫", "断更了"],
    ["看小说", "没时间看完"],
    ["做PPT", "格式错误"],
    ["练习舞蹈", "动作僵硬"],
    ["做面膜", "过敏了"],
    ["刷oj", "全部爆空间"],
    ["刷题", "全部不通过"],
    ["玩Linux", "Kernel Panic!!!"],
    ["上课", "听不懂"],
    ["考试", "考的全废"],
]
TooLucky = ["大吉", "吉吉吉", "贼吉", "特吉"]
TooUnLucky = ["大凶", "极凶"]
Lucky = ["小吉", "中吉", "中平", "有点吉", *TooLucky]
UnLucky = ["凶", "小凶", *TooUnLucky]
Fortune_List = Lucky + UnLucky
Bold_Font = str(
    Path(os.path.dirname(os.path.abspath(__file__)))
    / "ttf"
    / "SourceHanSansCN-Bold.otf"
)
Normal_Font = str(
    Path(os.path.dirname(os.path.abspath(__file__)))
    / "ttf"
    / "SourceHanSansCN-Normal.otf"
)
bg_size = (400, 350)


def get_image(nickname: str) -> bytes:
    # 生成背景
    # Generating backgrounds
    img = Image.new("RGB", bg_size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # 导入字体
    # Importing Fonts
    Title_Font = ImageFont.truetype(font=Bold_Font, size=20)
    Fortune_Font = ImageFont.truetype(font=Bold_Font, size=60)
    Suitable_To_Do_Font_Bold = ImageFont.truetype(font=Bold_Font, size=16)
    Suitable_To_Do_Font = ImageFont.truetype(font=Normal_Font, size=16)
    Detail_Font = ImageFont.truetype(font=Normal_Font, size=12)
    # 初始化内容
    # Initial content
    card = "你今天"
    title = card + "的运势"
    fortune = "§ " + random.choice(Fortune_List) + " §"
    fortune_width = Fortune_Font.getbbox(fortune)[2]
    suitable_to_do, detail = random.choice(
        [["诸事不宜", "在家躺一天"]] if fortune[2:-2] in TooUnLucky else todolist
    )
    suitable_to_do, detail = (
        textwrap.fill(suitable_to_do, width=8),
        textwrap.fill(detail, width=12),
    )

    unsuitable_to_do, detail2 = random.choice(
        [["诸事皆宜", "去做想做的事情吧"]] if fortune[2:-2] in TooLucky else nottodolist
    )
    unsuitable_to_do, detail2 = (
        textwrap.fill(unsuitable_to_do, width=8),
        textwrap.fill(detail2, width=12),
    )
    while unsuitable_to_do == suitable_to_do:
        unsuitable_to_do, detail2 = random.choice(
            [["诸事皆宜", "去做想做的事情吧"]]
            if fortune[2:-2] in TooLucky
            else nottodolist
        )
        unsuitable_to_do, detail2 = (
            textwrap.fill(unsuitable_to_do, width=8),
            textwrap.fill(detail2, width=12),
        )

    suitable_to_do2, detail3 = random.choice(
        [["", ""]] if fortune[2:-2] in TooUnLucky else todolist
    )
    suitable_to_do2, detail3 = (
        textwrap.fill(suitable_to_do2, width=8),
        textwrap.fill(detail3, width=12),
    )
    while suitable_to_do2 == suitable_to_do or suitable_to_do2 == unsuitable_to_do:
        suitable_to_do2, detail3 = random.choice(
            [["", ""]] if fortune[2:-2] in TooUnLucky else todolist
        )
        suitable_to_do2, detail3 = (
            textwrap.fill(suitable_to_do2, width=8),
            textwrap.fill(detail3, width=12),
        )

    unsuitable_to_do2, detail4 = random.choice(
        [["", ""]] if fortune[2:-2] in TooLucky else nottodolist
    )
    unsuitable_to_do2, detail4 = (
        textwrap.fill(unsuitable_to_do2, width=8),
        textwrap.fill(detail4, width=12),
    )
    while (
        unsuitable_to_do2 == suitable_to_do
        or unsuitable_to_do2 == unsuitable_to_do
        or unsuitable_to_do2 == suitable_to_do2
    ):
        unsuitable_to_do2, detail4 = random.choice(
            [["", ""]] if fortune[2:-2] in TooLucky else nottodolist
        )
        unsuitable_to_do2, detail4 = (
            textwrap.fill(unsuitable_to_do2, width=8),
            textwrap.fill(detail4, width=12),
        )
    ttd_width = (
        Suitable_To_Do_Font.getbbox(
            ("" if fortune[2:-2] in TooUnLucky else " " * 6) + suitable_to_do
        )[2]
        if len(suitable_to_do) <= 8
        else 152
    )
    tntd_width = (
        Suitable_To_Do_Font.getbbox(
            ("" if fortune[2:-2] in TooLucky else " " * 6) + unsuitable_to_do
        )[2]
        if len(unsuitable_to_do) <= 8
        else 152
    )
    ttd_width2 = (
        Suitable_To_Do_Font.getbbox(" " * 6 + suitable_to_do2)[2]
        if len(suitable_to_do2) <= 8
        else 152
    )
    tntd_width2 = (
        Suitable_To_Do_Font.getbbox(" " * 6 + unsuitable_to_do2)[2]
        if len(unsuitable_to_do2) <= 8
        else 152
    )
    detail_width = Detail_Font.getbbox(detail)[2] if len(detail) <= 12 else 144
    detail2_width = Detail_Font.getbbox(detail2)[2] if len(detail2) <= 12 else 144
    detail3_width = Detail_Font.getbbox(detail3)[2] if len(detail3) <= 12 else 144
    detail4_width = Detail_Font.getbbox(detail4)[2] if len(detail4) <= 12 else 144
    name_width = Title_Font.getbbox(title)[2]
    # 绘制
    # Draw
    draw.text(
        xy=(bg_size[0] / 2 - name_width / 2, 10),
        text=title,
        fill="#000000",
        font=Title_Font,
    )
    draw.text(
        xy=(bg_size[0] / 2 - fortune_width / 2, 50),
        text=fortune,
        fill="#e74c3c" if fortune[2:-2] in Lucky else "#3f3f3f",
        font=Fortune_Font,
    )
    begin_pos_y = 150
    draw.text(
        xy=(bg_size[0] / 4 - ttd_width / 2, begin_pos_y),
        text="诸事不宜" if fortune[2:-2] in TooUnLucky else "宜:",
        fill="#e74c3c",
        font=Suitable_To_Do_Font_Bold,
    )
    draw.text(
        xy=(bg_size[0] / 4 - ttd_width / 2, begin_pos_y),
        text="" if fortune[2:-2] in TooUnLucky else " " * 6 + suitable_to_do,
        fill="#e74c3c",
        font=Suitable_To_Do_Font,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - tntd_width / 2, begin_pos_y),
        text="诸事皆宜" if fortune[2:-2] in TooLucky else "忌:",
        fill="#000000",
        font=Suitable_To_Do_Font_Bold,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - tntd_width / 2, begin_pos_y),
        text="" if fortune[2:-2] in TooLucky else " " * 6 + unsuitable_to_do,
        fill="#000000",
        font=Suitable_To_Do_Font,
    )
    len_ttd = len(suitable_to_do.split("\n"))
    begin_pos_y += 25 + 25 * (len_ttd - 1)
    draw.text(
        xy=(bg_size[0] / 4 - detail_width / 2, begin_pos_y),
        text=detail,
        fill="#7f7f7f",
        font=Detail_Font,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - detail2_width / 2, begin_pos_y),
        text=detail2,
        fill="#7f7f7f",
        font=Detail_Font,
    )

    begin_pos_y = 250
    draw.text(
        xy=(bg_size[0] / 4 - ttd_width2 / 2, begin_pos_y),
        text="" if fortune[2:-2] in TooUnLucky else "宜:",
        fill="#e74c3c",
        font=Suitable_To_Do_Font_Bold,
    )
    draw.text(
        xy=(bg_size[0] / 4 - ttd_width2 / 2, begin_pos_y),
        text=" " * 6 + suitable_to_do2,
        fill="#e74c3c",
        font=Suitable_To_Do_Font,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - tntd_width2 / 2, begin_pos_y),
        text="" if fortune[2:-2] in TooLucky else "忌:",
        fill="#000000",
        font=Suitable_To_Do_Font_Bold,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - tntd_width2 / 2, begin_pos_y),
        text=" " * 6 + unsuitable_to_do2,
        fill="#000000",
        font=Suitable_To_Do_Font,
    )
    len_ttd2 = len(suitable_to_do2.split("\n"))
    begin_pos_y += 25 + 25 * (len_ttd2 - 1)
    draw.text(
        xy=(bg_size[0] / 4 - detail3_width / 2, begin_pos_y),
        text=detail3,
        fill="#7f7f7f",
        font=Detail_Font,
    )
    draw.text(
        xy=(bg_size[0] / 4 * 3 - detail4_width / 2, begin_pos_y),
        text=detail4,
        fill="#7f7f7f",
        font=Detail_Font,
    )
    return image_to_base64(img) # type: ignore
