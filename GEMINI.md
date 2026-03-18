# VSingerBoard 项目上下文 (Instructional Context)

## 项目概览
**VSingerBoard (点歌姬)** 是一款专为虚拟主播和歌手设计的跨平台桌面点歌管理面板。它能够实时抓取 Bilibili 和 抖音 直播间的弹幕，将点歌请求转化为有序、可交互的列表。

- **核心架构**: 基于 **Flet** (Flutter for Python) 构建的跨平台桌面应用。
- **UI 风格**: 现代化 Material Design 风格，支持亮色/暗色模式。
- **数据持久化**: 使用 **Tortoise-ORM** 配合 **SQLite** 存储本地数据。
- **并发模型**: 采用异步 I/O (`asyncio`) 处理弹幕抓取和后台任务。

## 技术栈
- **语言**: Python 3.12+
- **UI 框架**: [Flet](https://flet.dev/)
- **ORM**: Tortoise-ORM (配合 Aerich 进行迁移管理)
- **网络与协议**: `aiohttp`, `curl-cffi`, `betterproto2` (Protobuf)
- **直播对接**: Bilibili API (`bilibili-api-python`), 抖音自定义 WebSocket 实现
- **打包**: PyInstaller (通过 `flet pack` 调用)
- **包管理**: [uv](https://docs.astral.sh/uv/)

## 关键目录结构
- `src/ui/`: UI 层。包含 `layout.py` (主布局)、`pages/` (各功能页面) 和 `components/` (通用组件)。
- `src/manager/`: 核心管理器。管理应用生命周期、后台任务、消息分发及订阅逻辑。
- `src/database/`: 数据持久化。包含 `model.py` (定义模型) 和 `db.py` (封装数据库操作)。
- `src/live/`: 直播适配层。实现各平台弹幕抓取的具体逻辑。
- `src/utils/`: 通用工具。日志、异步工作流、路径处理（`tool.py`）等。
- `assets/`: 静态资源（图标、字体、JS 签名库、图片等）。
- `hooks/`: PyInstaller 打包钩子与运行时钩子。

## 开发规范与约定
1. **异步优先**: 核心业务逻辑必须使用 `async/await`，确保 UI 线程不被阻塞。
2. **资源路径**: 必须通过 `src/utils/tool.py` 中的 `resource_path` 函数访问 `assets/` 资源，以适配打包环境。
3. **分层原则**: UI 页面应通过 `src.database.db.Db` 类操作数据，严禁在页面代码中直接编写复杂的 ORM 查询。
4. **日志记录**: 使用 `src.utils.logger` 记录关键信息，日志信息建议使用英文。
5. **代码注释**: 遵循项目习惯，**代码内部注释使用中文**。
6. **版本管理**: 版本号定义在 `pyproject.toml` 的 `version` 字段，打包脚本 `pack.sh` 会自动同步至代码中。

## 常用开发命令
### 环境与运行
```bash
# 安装依赖
uv sync
# 启动开发服务器
uv run flet run main.py
```

### 数据库迁移 (Aerich)
```bash
# 生成迁移文件 (如有模型变动)
uv run aerich migrate --name <describe_change>
# 应用迁移
uv run aerich upgrade
```

### 打包构建
```bash
# 执行全平台/特定平台打包脚本
bash pack.sh
```

## 协作注意事项
- **环境依赖**: 确保本地已安装 `uv`。部分签名逻辑可能依赖 Node.js 环境（通过 `pyexecjs` 或 `quickjs`）。
- **同步更新**: 修改 `pyproject.toml` 或数据库模型后，请务必更新此文档或运行相应的迁移命令。
