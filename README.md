# MP4 Frame Extractor

A desktop GUI tool for extracting frames from MP4 video files, with bilingual (EN/ZH) support.

> 📖 [中文介绍](README_zh.md)

## Features

- 🎬 Select an MP4 video file and view video metadata (total frames, FPS)
- 📁 Choose a custom output directory for extracted frames
- ⚙️ Configure frame interval (extract every N frames)
- 🖼️ Output in JPEG or PNG format
- 📊 Real-time progress bar
- 🚫 Cancel extraction at any time
- 🌐 Bilingual UI — English (default) / Chinese toggle

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager
- Python >= 3.11, < 3.14

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd mv

# 2. Install Python 3.11 and create virtual environment
uv python install 3.11
uv venv --python 3.11

# 3. Install dependencies
uv sync

# 4. Run
.venv\Scripts\python.exe main.py
```

## Build Standalone Executable

```bash
# PyInstaller is included in dev dependencies
.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name "mp4-frame-extractor" main.py

# Output: dist/mp4-frame-extractor.exe (~59 MB)
```

The resulting `.exe` is fully self-contained and can run on any **Windows 10/11 64-bit** machine without Python installed.

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python-headless` | Video frame reading and image writing |
| `pyinstaller` | Build standalone `.exe` (dev only) |
| `tkinter` | GUI toolkit (bundled with Python) |

## Project Structure

```
mv/
├── main.py              # Application entry point (GUI + frame extraction)
├── pyproject.toml        # Project metadata and dependencies
├── requirements.txt      # Locked dependency versions with hashes
├── CLAUDE.md             # Project documentation for AI assistants
├── README.md             # This file
├── README_zh.md          # Chinese version
└── .gitignore
```

## License

MIT
