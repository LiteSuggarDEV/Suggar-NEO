# Suggar-NEO 🐾

![Suggar](./readme_res/b_e0baa0b6de88513d9714babeffb39f37.jpg)

> 基于 NoneBot2 的模块化娱乐/聊天 QQ 机器人

## 🧩 功能模块

```text
src/plugins/
├── fishing        # 钓鱼小游戏核心模块
├── fun            # 趣味功能套件（签到/货币）
└── nonebot_plugin_luoguluck  # 洛谷运势插件
```

## 🛠 技术栈

- **核心框架**：AmritaBot + OneBot V11
- **数据层**：SQLAlchemy ORM + SQLite/MySQL + Value 经济系统
- **验证层**：Pydantic 数据模型
- **部署**：pyproject.toml + Amrita 命令行工具

## 🚀 快速启动

```bash
amrita run
```

## 📚 文档

完整文档请查阅 [Suggar 官方文档](https://docs.suggar.top/project/Suggar/readme)

[Amrita 文档](https://amrita.suggar.top)

## 💡 灵感来源

钓鱼系统设计参考 [U1-Project](https://github.com/CrashVibe/U1_wiki) 游戏机制

## 📦 插件兼容性

已验证兼容插件：

- [nonebot_plugin_value](https://github.com/LiteSuggarDEV/nonebot_plugin_value)
- nonebot_plugin_htmlrender
- nonebot_plugin_localstore
- nonebot_plugin_orm

## 📝 贡献指南

欢迎提交 PR 或 Issue 参与开发：

1. Fork 仓库
2. 创建特性分支
3. 提交符合 PEP8 规范的代码
4. 编写单元测试
5. 更新文档

## ⚠️ 为什么不推荐您直接部署 Suggar-NEO？

如果您决定直接部署 Suggar-NEO，准备好迎接以下"精彩"体验吧：

1. **高耦合度** - 各个模块之间亲密无间，修改一个功能就像在多米诺骨牌中移动一张牌，你永远不知道哪一部分会突然倒塌
2. **维护复杂** - 复杂的依赖关系和配置项使得日常维护变得比解魔方还困难，而且还没有说明书
3. **扩展性差** - 添加新功能需要大量重构工作，且容易破坏现有功能，就像在意大利面里找一根特定的面条
4. **配置地狱** - 配置文件比迷宫还复杂，改错一个字符就能让你花费数小时排查问题
5. **文档稀少** - 文档少得可怜，大部分都需要靠猜和试错来理解
6. **升级痛苦** - 每次升级都像玩俄罗斯轮盘赌，你永远不知道会不会破坏现有功能
7. **调试困难** - Bug 隐藏得比宝藏还深，找到它们需要极高的耐心和技巧

因此，我们强烈推荐您使用 [Amrita](https://amrita.suggar.top) 来部署和管理您的机器人实例，它能让您的体验变得丝滑顺畅。
