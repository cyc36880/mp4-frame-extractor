# MP4 视频取帧工具

从 MP4 视频文件中提取帧图片的桌面 GUI 工具，支持中英文双语切换。

## 功能

- 🎬 选择 MP4 视频文件并显示视频信息（总帧数、FPS）
- 📁 自定义图片输出目录
- ⚙️ 设置帧间隔（每 N 帧取一张）
- 🖼️ 支持 JPEG / PNG 输出格式
- 📊 实时进度条显示
- 🚫 随时取消提取
- 🌐 中英文界面切换（默认英文）

## 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url>
cd mv

# 2. 安装 Python 3.11 并创建虚拟环境
uv python install 3.11
uv venv --python 3.11
uv sync

# 3. 运行
.venv\Scripts\python.exe main.py
```

## 构建可执行文件

```bash
# 安装打包工具（已包含在 dev 依赖中）
# 构建单文件 exe
.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name "mp4-frame-extractor" main.py

# 输出文件：dist/mp4-frame-extractor.exe
```

## 依赖

| 包 | 用途 |
|---|---|
| opencv-python-headless | 视频帧读取与图片保存 |
| pyinstaller | 打包为独立 exe |
| tkinter | GUI 界面（Python 内置） |

## 环境要求

- Python >= 3.11, < 3.14
- Windows 10/11 64-bit（打包后的 exe 也仅支持 Windows）
- 使用 [uv](https://docs.astral.sh/uv/) 管理依赖
