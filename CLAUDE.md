# CLAUDE.md

## Project Identity

**MP4 Frame Extractor** — a single-file desktop GUI application that extracts image frames from MP4 video files. Built with Python, tkinter, and OpenCV, packable as a standalone Windows `.exe`.

## Purpose & Goals

- Provide a simple, intuitive GUI for non-technical users to extract frames from videos
- Support bilingual UI (English default, Chinese toggle) for a mixed-language user base
- Produce a single self-contained `.exe` (~59 MB) that runs on Windows 10/11 without any Python installation

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| GUI | `tkinter` (stdlib) | Zero extra dependencies, small footprint, sufficient for form-based tools |
| Video I/O | `opencv-python-headless` | Industry standard for video read/write, headless variant avoids Qt/GUI bloat |
| Package manager | `uv` (by Astral) | Fast resolver, PEP 621 pyproject.toml, Python version management |
| Packager | `PyInstaller` (dev dep) | `--onefile --windowed` produces a single portable `.exe` |
| Python version | **3.11** (pinned via `.python-version` and `requires-python = ">=3.11,<3.14"`) | 3.14 broke Qt/PyQt compatibility for a previously bundled annotation tool; 3.11 is stable and widely available |

## Architecture

Single-file app: everything lives in `main.py` (~370 lines).

```
main.py
├── TEXTS dict (module-level)         # i18n: 31+ keys × 2 languages (en, zh)
├── VideoFrameExtractor(tk.Tk)        # Main window class
│   ├── .t(key, **kwargs)             # Translation lookup + format
│   ├── ._build_ui()                  # Layout all widgets (7 rows)
│   ├── ._refresh_ui()                # Update widget texts on language switch
│   ├── ._browse_video()              # filedialog → load video metadata
│   ├── ._browse_output_dir()         # filedialog → choose output folder
│   ├── ._start_extract()             # Validate → launch worker thread
│   ├── ._extract_frames()            # Worker thread: cv2.VideoCapture loop
│   ├── ._update_progress()           # .after() callback from thread → UI
│   └── ._extract_done()              # Completion callback → messagebox
└── if __name__ == "__main__"         # Entry point
```

### Key Design Decisions

1. **Threaded extraction** — `_extract_frames()` runs in a `threading.Thread` (daemon) so the GUI stays responsive. UI updates are marshalled to the main thread via `.after(0, callback)`.

2. **Progress throttling** — progress updates fire every 10 frames (`count % 10 == 0`) to avoid flooding the tkinter event queue with `.after()` calls.

3. **Graceful cancellation** — `self.running` boolean flag. Worker thread checks it each loop iteration. `_on_close()` sets `running = False` before destroying the window.

4. **i18n without gettext** — pure Python dictionary (`TEXTS`). `self.t(key, **kwargs)` does lookup + `str.format()`. Language toggle rebinds all widget texts via `_refresh_ui()` without destroying/recreating widgets.

5. **No external i18n files** — all strings are inline in the `TEXTS` dict. This keeps the exe self-contained (no missing `.mo`/`.po` files at runtime).

6. **Custom filename prefix** — a user-editable `ttk.Entry` (default `"frame"`) sets the output filename prefix. Falls back to `"frame"` when left blank. Output pattern: `{prefix}_{idx:06d}.{fmt}` (e.g. `myscene_000001.jpg`).

## File Structure

```
mv/
├── main.py              # Application entry point (GUI + frame extraction)
├── pyproject.toml        # PEP 621 metadata, dependencies, uv config
├── requirements.txt      # `uv export` output: locked versions with SHA256 hashes
├── uv.lock               # uv lockfile for reproducible installs
├── .python-version       # Pin Python version for uv (3.11)
├── .gitignore            # Exclude venv, build/, dist/, IDE files
├── CLAUDE.md             # This file
├── README.md             # English documentation
├── README_zh.md          # Chinese documentation
└── test.mp4              # Test video (231 frames, 32.26 FPS, 240×320)
```

## I18n System

`TEXTS` is a module-level dict with two sub-dicts (`"en"`, `"zh"`), each containing 31+ string keys.

### Static strings
Direct lookup: `self.t("browse")` → `"Browse..."` / `"浏览…"`

### Dynamic strings (templates)
Use `str.format` placeholders:
```python
self.t("progress", current=50, total=100, pct=50)
# → "Processed 50/100 frames (50%)" / "已处理 50/100 帧 (50%)"
```

### Adding a new language
Add a sub-dict under a new key (e.g. `"ja"`) to `TEXTS`, with all 31+ keys translated. No code changes needed.

## Build & Packaging

### Development
```bash
uv python install 3.11
uv venv --python 3.11
uv sync
.venv\Scripts\python.exe main.py
```

### Production build
```bash
.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name "mp4-frame-extractor" main.py
# → dist/mp4-frame-extractor.exe (~59 MB)
```

### Rebuilding environment from scratch
```bash
uv sync                              # uses pyproject.toml + uv.lock
# or
uv pip install -r requirements.txt   # uses locked hashes
```

## Key Dependencies

| Package | Version | Notes |
|---|---|---|
| opencv-python-headless | 4.13.x | `headless` variant — no Qt, no GUI deps |
| numpy | 2.4.x | OpenCV dependency |
| pyinstaller | 6.21.x | Dev only; `--windowed` hides console |

## Known Constraints

1. **Python version** — must be `>=3.11,<3.14`. Python 3.14 has no PyQt5 wheels (relevant if labelImg annotation tool is ever re-added).
2. **Windows only** — PyInstaller builds target Windows. tkinter and OpenCV work cross-platform, but packaging and path separators (`\`) assume Windows.
3. **MP4 only** — file dialog filters for `*.mp4`. OpenCV can read other formats; to support them, update `filetypes` in `_browse_video()`.
4. **Memory** — all frames are processed sequentially via `cv2.VideoCapture.read()`, not loaded into memory at once. Suitable for large videos.

## Previous Iterations (Historical Context)

- **v0.1**: Basic frame extractor, Chinese-only, Python 3.14
- **v0.2**: Added i18n EN/ZH support, language toggle button
- **v0.3**: Downgraded to Python 3.11, added launcher + labelImg integration — removed due to labelImg stability issues (PyQt packaging, Open Dir crash)
- **v0.4**: Clean single-file frame extractor, Python 3.11, bilingual
- **v0.5 (current)**: Added custom filename prefix input; window resized to 680×420

## Development Conventions

- Keep `main.py` self-contained (single file) unless a feature adds >500 lines
- All user-facing strings go through `TEXTS` / `self.t()`
- Worker tasks run in daemon threads, UI updates use `.after()`
- Test with `test.mp4` (231 frames, ~7 seconds of video)
- Prefer `uv` for all package operations
- Use `\` path separators (Windows)
