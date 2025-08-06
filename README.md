# Suggar-NEO 🐾

![Suggar](./readme_res/b_e0baa0b6de88513d9714babeffb39f37.jpg)

> 基于 NoneBot2 的模块化娱乐/聊天 QQ 机器人

## 🧩 功能模块

```
src/plugins/
├── fishing        # 钓鱼小游戏核心模块
├── manager        # 群组管理工具集
├── menu           # HTML交互菜单系统
├── fun            # 趣味功能套件（签到/货币）
├── status         # 运行状态监控
└── nonebot_plugin_luoguluck  # 洛谷运势插件
```

## 🛠 技术栈

- **核心框架**：NoneBot2 + CQHTTP
- **数据层**：SQLAlchemy ORM + SQLite/MySQL + Value 经济系统
- **验证层**：Pydantic 数据模型
- **部署**：pyproject.toml + nb 命令行工具

## 🚀 快速启动

```bash
uv run ./bot.py
```

## 📚 文档

完整文档请查阅 [Suggar 官方文档](https://docs.suggar.top/project/Suggar/readme)

## 💡 灵感来源

钓鱼系统设计参考 [U1-Project](https://github.com/CrashVibe/U1_wiki) 游戏机制

## 📦 插件兼容性

已验证兼容插件：

- [nonebot_plugin_value](https://github.com/LiteSuggarDEV/nonebot_plugin_value)
- [nonebot_plugin_suggarchat](https://github.com/LiteSuggarDEV/nonebot_plugin_suggarchat)
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
