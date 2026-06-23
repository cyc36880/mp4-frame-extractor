#!/usr/bin/env python3
"""MP4 video frame extractor — GUI tool with bilingual (EN/ZH) support."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2

# ── i18n dictionary ─────────────────────────────────────────────

TEXTS = {
    "en": {
        "title": "MP4 Frame Extractor",
        "video_file": "Video File:",
        "output_dir": "Output Dir:",
        "interval": "Interval:",
        "interval_hint": "(every N frames, 1=all)",
        "format_label": "Format:",
        "browse": "Browse...",
        "start": "Start Extract",
        "cancel": "Cancel",
        "toggle_lang": "中文",
        "no_video": "No video file selected",
        "ready": "Ready",
        "extracting": "Extracting...",
        "cancelling": "Cancelling...",
        "warn_title": "Notice",
        "error_title": "Error",
        "select_video_first": "Please select a video file first.",
        "select_dir_first": "Please select an output directory first.",
        "file_not_found": "Video file not found. Please re-select.",
        "cannot_open": "Cannot open video file.",
        "done_title": "Extraction Complete",
        "open_video_title": "Select MP4 Video File",
        "mp4_videos": "MP4 Videos",
        "all_files": "All Files",
        "output_dir_title": "Select Output Directory",
        "video_info": (
            "Total: {total}  |  FPS: {fps:.2f}  |  "
            "Every {interval} frames -> ~{estimated} images"
        ),
        "progress": "Processed {current}/{total} frames ({pct}%)",
        "done_msg": "Done! Saved {saved} images to:\n{output_dir}",
        "cancelled_msg": "Cancelled. Saved {saved} images to:\n{output_dir}",
        "done_status": "Done - {saved} images saved",
        "cancelled_status": "Cancelled",
        "cancelled_no_save": "Cancelled, no images saved",
        "cannot_read": "Cannot read this video file",
    },
    "zh": {
        "title": "MP4 视频取帧工具",
        "video_file": "视频文件：",
        "output_dir": "输出目录：",
        "interval": "帧间隔：",
        "interval_hint": "（每 N 帧取一张，1=逐帧）",
        "format_label": "图片格式：",
        "browse": "浏览…",
        "start": "开始提取",
        "cancel": "取消",
        "toggle_lang": "EN",
        "no_video": "尚未选择视频文件",
        "ready": "就绪",
        "extracting": "正在提取…",
        "cancelling": "正在取消…",
        "warn_title": "提示",
        "error_title": "错误",
        "select_video_first": "请先选择视频文件。",
        "select_dir_first": "请先选择输出目录。",
        "file_not_found": "视频文件不存在，请重新选择。",
        "cannot_open": "无法打开视频文件。",
        "done_title": "提取完成",
        "open_video_title": "选择 MP4 视频文件",
        "mp4_videos": "MP4 视频",
        "all_files": "所有文件",
        "output_dir_title": "选择图片输出目录",
        "video_info": (
            "总帧数: {total}  |  FPS: {fps:.2f}  |  "
            "每 {interval} 帧取一张 -> 预计 {estimated} 张图片"
        ),
        "progress": "已处理 {current}/{total} 帧 ({pct}%)",
        "done_msg": "提取完成！共保存 {saved} 张图片到：\n{output_dir}",
        "cancelled_msg": "已取消。共保存 {saved} 张图片到：\n{output_dir}",
        "done_status": "完成 - 共保存 {saved} 张图片",
        "cancelled_status": "已取消",
        "cancelled_no_save": "已取消，未保存图片",
        "cannot_read": "无法读取该视频文件",
    },
}


class VideoFrameExtractor(tk.Tk):
    """Main window: full GUI for MP4 frame extraction with bilingual support."""

    def __init__(self):
        super().__init__()
        self.lang = "en"

        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.interval = tk.IntVar(value=30)
        self.image_format = tk.StringVar(value="jpg")
        self.running = False
        self.worker_thread = None

        self._center_window()
        self._build_ui()

    # ── helpers ────────────────────────────────────────────────

    def t(self, key, **kwargs):
        text = TEXTS[self.lang].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"680x380+{x}+{y}")

    # ── UI ─────────────────────────────────────────────────────

    def _build_ui(self):
        self.title(self.t("title"))
        self.resizable(False, False)
        pad = {"padx": 12, "pady": 6}

        # ---- 1. video file ----
        row1 = ttk.Frame(self)
        row1.pack(fill=tk.X, **pad)
        self.lbl_video = ttk.Label(row1, text=self.t("video_file"), width=10)
        self.lbl_video.pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.video_path, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )
        self.btn_video = ttk.Button(row1, text=self.t("browse"), command=self._browse_video)
        self.btn_video.pack(side=tk.RIGHT)

        # ---- 2. output dir ----
        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, **pad)
        self.lbl_dir = ttk.Label(row2, text=self.t("output_dir"), width=10)
        self.lbl_dir.pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.output_dir, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )
        self.btn_dir = ttk.Button(row2, text=self.t("browse"), command=self._browse_output_dir)
        self.btn_dir.pack(side=tk.RIGHT)

        # ---- 3. params ----
        row3 = ttk.Frame(self)
        row3.pack(fill=tk.X, **pad)
        self.lbl_interval = ttk.Label(row3, text=self.t("interval"), width=10)
        self.lbl_interval.pack(side=tk.LEFT)
        ttk.Spinbox(row3, textvariable=self.interval, from_=1, to=9999, width=8).pack(
            side=tk.LEFT
        )
        self.lbl_hint = ttk.Label(row3, text=self.t("interval_hint"))
        self.lbl_hint.pack(side=tk.LEFT, padx=(4, 20))
        self.lbl_fmt = ttk.Label(row3, text=self.t("format_label"))
        self.lbl_fmt.pack(side=tk.LEFT)
        ttk.Combobox(
            row3, textvariable=self.image_format, values=["jpg", "png"],
            state="readonly", width=6,
        ).pack(side=tk.LEFT)

        # ---- 4. video info ----
        self.info_label = ttk.Label(self, text=self.t("no_video"), foreground="gray")
        self.info_label.pack(fill=tk.X, **pad)

        # ---- 5. progress ----
        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.pack(fill=tk.X, padx=12, pady=(6, 2))
        self.status_label = ttk.Label(self, text=self.t("ready"), foreground="gray")
        self.status_label.pack(fill=tk.X, padx=12)

        # ---- 6. buttons ----
        row6 = ttk.Frame(self)
        row6.pack(fill=tk.X, **pad)
        self.start_btn = ttk.Button(row6, text=self.t("start"), command=self._start_extract)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.cancel_btn = ttk.Button(
            row6, text=self.t("cancel"), command=self._cancel_extract, state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT)
        self.lang_btn = ttk.Button(
            row6, text=self.t("toggle_lang"), command=self._toggle_language, width=4
        )
        self.lang_btn.pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── language ───────────────────────────────────────────────

    def _toggle_language(self):
        self.lang = "zh" if self.lang == "en" else "en"
        self._refresh_ui()

    def _refresh_ui(self):
        self.title(self.t("title"))
        self.lbl_video.config(text=self.t("video_file"))
        self.btn_video.config(text=self.t("browse"))
        self.lbl_dir.config(text=self.t("output_dir"))
        self.btn_dir.config(text=self.t("browse"))
        self.lbl_interval.config(text=self.t("interval"))
        self.lbl_hint.config(text=self.t("interval_hint"))
        self.lbl_fmt.config(text=self.t("format_label"))
        self.start_btn.config(text=self.t("start"))
        self.cancel_btn.config(text=self.t("cancel"))
        self.lang_btn.config(text=self.t("toggle_lang"))
        if self.running:
            self.status_label.config(text=self.t("extracting"), foreground="black")
        elif self.video_path.get():
            self._update_video_info(self.video_path.get())
        else:
            self.info_label.config(text=self.t("no_video"), foreground="gray")
            self.status_label.config(text=self.t("ready"), foreground="gray")

    # ── file choosers ──────────────────────────────────────────

    def _browse_video(self):
        path = filedialog.askopenfilename(
            title=self.t("open_video_title"),
            filetypes=[(self.t("mp4_videos"), "*.mp4"), (self.t("all_files"), "*.*")],
        )
        if path:
            self.video_path.set(path)
            self._update_video_info(path)

    def _browse_output_dir(self):
        path = filedialog.askdirectory(title=self.t("output_dir_title"))
        if path:
            self.output_dir.set(path)

    def _update_video_info(self, path):
        cap = cv2.VideoCapture(path)
        if cap.isOpened():
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            interval = self.interval.get()
            estimated = max(1, total // interval)
            self.info_label.config(
                text=self.t("video_info", total=total, fps=fps,
                             interval=interval, estimated=estimated),
                foreground="black",
            )
        else:
            self.info_label.config(text=self.t("cannot_read"), foreground="red")

    # ── extract control ────────────────────────────────────────

    def _start_extract(self):
        if not self.video_path.get():
            messagebox.showwarning(self.t("warn_title"), self.t("select_video_first"))
            return
        if not self.output_dir.get():
            messagebox.showwarning(self.t("warn_title"), self.t("select_dir_first"))
            return
        if not os.path.exists(self.video_path.get()):
            messagebox.showerror(self.t("error_title"), self.t("file_not_found"))
            return

        os.makedirs(self.output_dir.get(), exist_ok=True)
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self.status_label.config(text=self.t("extracting"), foreground="black")
        self.worker_thread = threading.Thread(target=self._extract_frames, daemon=True)
        self.worker_thread.start()

    def _cancel_extract(self):
        self.running = False
        self.status_label.config(text=self.t("cancelling"), foreground="orange")

    def _on_close(self):
        self.running = False
        self.destroy()

    # ── frame extraction (worker thread) ───────────────────────

    def _extract_frames(self):
        video_path = self.video_path.get()
        output_dir = self.output_dir.get()
        interval = self.interval.get()
        fmt = self.image_format.get()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.after(0, self._extract_done, False, self.t("cannot_open"), 0)
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0
        saved = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            if count % interval == 0:
                filename = f"frame_{saved:06d}.{fmt}"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
                saved += 1
            count += 1
            if count % 10 == 0:
                self.after(0, self._update_progress, count, total_frames)

        cap.release()
        self.after(0, self._update_progress, count, total_frames)

        if self.running:
            self.after(0, self._extract_done, True,
                       self.t("done_msg", saved=saved, output_dir=output_dir), saved)
        else:
            self.after(0, self._extract_done, False,
                       self.t("cancelled_msg", saved=saved, output_dir=output_dir), saved)

    # ── UI callbacks ───────────────────────────────────────────

    def _update_progress(self, current, total):
        if total > 0:
            pct = min(100, int(current / total * 100))
            self.progress["value"] = pct
            self.status_label.config(
                text=self.t("progress", current=current, total=total, pct=pct),
                foreground="black",
            )

    def _extract_done(self, success, message, saved_count):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        if success:
            self.progress["value"] = 100
            self.status_label.config(
                text=self.t("done_status", saved=saved_count), foreground="green"
            )
            messagebox.showinfo(self.t("done_title"), message)
        else:
            if saved_count > 0:
                self.status_label.config(
                    text=self.t("cancelled_status"), foreground="orange"
                )
            else:
                self.status_label.config(
                    text=self.t("cancelled_no_save"), foreground="gray"
                )


if __name__ == "__main__":
    VideoFrameExtractor().mainloop()
