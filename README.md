# VSingerBoard - 您的专属虚拟主播点歌台

![Build Status](https://github.com/zangxx66/VSingerBoard/actions/workflows/python-publish.yml/badge.svg) ![Python Version](https://img.shields.io/badge/python-3.12-blue.svg) ![License](https://img.shields.io/badge/license-GPL-green.svg)

---

> 您是否曾梦想过拥有一个能与观众实时互动、智能管理点歌的直播间？
> 
> 在弹幕的海洋中，手动记录每一个点歌请求不仅繁琐，更容易错失粉丝的热情。VSingerBoard 专为解决这一痛点而生，它是一座连接您与粉丝的桥梁，一个专为虚拟主播、歌手和音乐爱好者打造的、跨平台的智能点歌管理面板。

**VSingerBoard** 将混乱的弹幕请求，转化为一个优雅、有序、可交互的列表，让您专注于表演，而非手忙脚乱的管理。

## ✨ 核心功能

- 🎤 **多平台支持**: 已无缝接入 **Bilibili** 和 **抖音** 两大主流直播平台，未来更具扩展性。
- 🚀 **实时弹幕抓取**: 采用高性能异步框架，实时捕获并智能过滤点歌弹幕，不错过任何一个粉丝的热情。
- 🛡️ **强大的风控对抗**: 针对抖音平台，通过模拟执行浏览器签名算法和原生 WebSocket 通信，实现稳定、难以被检测的弹幕连接。
- 🎨 **精美UI界面**: 基于 Vue 3 和 Element Plus 打造的现代化、简洁美观的操作界面，支持亮色/暗色模式切换，带来极致的视觉享受。
- 🛠️ **一键式构建与部署**: 借助 GitHub Actions 实现全自动的跨平台（Windows, macOS, Linux）打包与发布，确保您随时能获取到最新的稳定版本。
- 🔒 **本地化数据存储**: 使用 Tortoise-ORM 和 SQLite，在本地安全地存储您的房间配置和登录凭据，无需担心隐私泄露。

## 📸 应用截图

*(在这里插入应用的精美截图，例如主界面、B站标签页、抖音标签页、设置页面等)*

![image](https://raw.githubusercontent.com/zangxx66/VSingerBoard/master/data/screenshot.png)

## 🚀 如何使用

对于普通用户，我们强烈建议您直接下载已打包好的应用程序。

1.  前往 [**GitHub Releases**](https://github.com/zangxx66/VSingerBoard/releases) 页面。
2.  下载适用于您操作系统（Windows, macOS, 或 Linux）的最新版本压缩包。
3.  解压后，直接运行主程序即可！

## 🛠️ 技术栈

- **后端**: Python 3.12, FastAPI, Uvicorn, Tortoise-ORM
- **前端**: Vue 3, Vite, Element Plus, TypeScript
- **桌面端框架**: Pywebview
- **构建与打包**: PyInstaller, GitHub Actions
- **直播平台接口**: `bilibili-api-python`, `websocket-client`, `py_mini_racer`, `Protobuf`

## 🤝 如何贡献

我们欢迎任何形式的贡献！无论是提交 Bug、建议新功能，还是直接贡献代码，都将是对这个项目的巨大支持。

1.  Fork 本仓库。
2.  创建您的新分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将您的分支推送到远程 (`git push origin feature/AmazingFeature`)。
5.  开启一个 Pull Request。

## 📄 许可证

本项目基于 GPL-3.0 许可证发布。详情请见 `LICENSE` 文件。
