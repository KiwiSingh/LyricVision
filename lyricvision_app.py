import os

# ==========================================
# SAFETY: Force CPU + MPS fallback
# ==========================================
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import keyring
import torch
from subtitle_export import export_srt

# ==========================================
# Torch load override (PyTorch 2.6+ fix)
# ==========================================
_original_torch_load = torch.load


def patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)


torch.load = patched_torch_load

# ==========================================
# Internal Imports
# ==========================================
from whisper_align import transcribe_with_word_timestamps
from demucs_utils import separate_vocals
from nlp_utils import extract_keywords
from video_search import VideoSearch
from audio_analysis import detect_bpm
from timeline_builder import build_word_level_timeline
from davinci_export import export_fcpxml

APP_NAME = "LyricVision"


class LyricVisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LyricVision")
        self.root.geometry("1000x950")

        self.audio_path = None
        self.bpm = None
        self.word_timestamps = []

        self.build_ui()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):
        ttk.Label(
            self.root,
            text="Lyrics (Optional if using WhisperX auto-alignment)"
        ).pack(anchor="w", padx=10, pady=5)

        self.lyrics_box = tk.Text(self.root, height=6)
        self.lyrics_box.pack(fill="x", padx=10)

        ttk.Button(self.root, text="Import Audio", command=self.load_audio).pack(pady=5)

        # Model
        ttk.Label(self.root, text="Keyword Model").pack(pady=(15, 0))
        self.model_var = tk.StringVar(value="gpt-4.1-mini")

        ttk.OptionMenu(
            self.root,
            self.model_var,
            "gpt-4.1-mini",
            "gpt-4.1-mini",
            "gpt-4o",
            "gemini-3-flash-preview"
        ).pack()

        ttk.Button(self.root, text="Manage API Keys",
                   command=self.open_key_manager).pack(pady=5)

        # BPM
        ttk.Label(self.root, text="BPM Settings").pack(pady=(15, 0))
        bpm_frame = ttk.Frame(self.root)
        bpm_frame.pack(pady=5)

        self.manual_bpm_var = tk.StringVar()
        self.use_manual_bpm_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            bpm_frame,
            text="Use Manual BPM",
            variable=self.use_manual_bpm_var
        ).grid(row=0, column=0, padx=5)

        ttk.Entry(
            bpm_frame,
            textvariable=self.manual_bpm_var,
            width=10
        ).grid(row=0, column=1, padx=5)

        # WhisperX
        self.use_whisper_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.root,
            text="Use WhisperX Word Alignment (CPU)",
            variable=self.use_whisper_var
        ).pack(pady=5)

        # Resolution
        self.resolution_var = tk.StringVar(value="1080p")
        ttk.Label(self.root, text="Resolution").pack()
        ttk.OptionMenu(
            self.root,
            self.resolution_var,
            "1080p",
            "1080p",
            "4K"
        ).pack()

        # Subdivision
        ttk.Label(self.root, text="Beat Subdivision").pack(pady=(10, 0))
        self.subdivision_var = tk.StringVar(value="quarter")

        ttk.OptionMenu(
            self.root,
            self.subdivision_var,
            "quarter",
            "quarter",
            "eighth",
            "sixteenth"
        ).pack()

        ttk.Button(
            self.root,
            text="Generate Video Plan",
            command=self.run_pipeline
        ).pack(pady=20)

        self.status_label = ttk.Label(self.root, text="Idle")
        self.status_label.pack()

        ttk.Button(
            self.root,
            text="Export Beat-Snapped Subtitles (.srt)",
            command=self.export_subtitles
        ).pack(pady=10)        

    # =====================================================
    # API KEY MANAGER
    # =====================================================

    def open_key_manager(self):
        win = tk.Toplevel(self.root)
        win.title("API Key Manager")
        win.geometry("450x400")

        services = {
            "openai": ("OpenAI", "https://platform.openai.com/api-keys"),
            "gemini": ("Google Gemini", "https://ai.google.dev/"),
            "pexels": ("Pexels", "https://www.pexels.com/api/"),
            "pixabay": ("Pixabay", "https://pixabay.com/api/docs/")
        }

        for idx, (key_name, (label, url)) in enumerate(services.items()):
            ttk.Label(win, text=label).grid(row=idx * 2, column=0, sticky="w", padx=10, pady=5)

            current = keyring.get_password(APP_NAME, key_name) or ""
            entry = ttk.Entry(win, width=40)
            entry.insert(0, current)
            entry.grid(row=idx * 2, column=1, padx=10)

            def save_key(name=key_name, ent=entry):
                keyring.set_password(APP_NAME, name, ent.get())
                messagebox.showinfo("Saved", f"{name} key saved securely.")

            ttk.Button(win, text="Save", command=save_key).grid(row=idx * 2, column=2, padx=5)
            ttk.Button(win, text="Get Key",
                       command=lambda link=url: webbrowser.open(link)).grid(row=idx * 2 + 1, column=1, pady=5)

    # =====================================================
    # AUDIO
    # =====================================================

    def load_audio(self):
        self.audio_path = filedialog.askopenfilename(
            filetypes=[("Audio", "*.wav *.mp3 *.flac *.m4a")]
        )

        if not self.audio_path:
            return

        self.update_status("Detecting BPM...")

        try:
            detected_bpm = detect_bpm(self.audio_path)
            self.bpm = float(detected_bpm)
            self.manual_bpm_var.set(str(round(self.bpm, 2)))
            messagebox.showinfo("BPM Detected",
                                f"Detected BPM: {round(self.bpm, 2)}")
        except Exception as e:
            messagebox.showerror("BPM Error", str(e))
            self.bpm = None

    # =====================================================
    # PIPELINE
    # =====================================================

    def run_pipeline(self):
        threading.Thread(target=self._pipeline_thread, daemon=True).start()

    def _pipeline_thread(self):
        try:

            if not self.audio_path:
                self._safe_msg("Missing Audio", "Please import audio first.")
                return

            if self.use_manual_bpm_var.get():
                try:
                    self.bpm = float(self.manual_bpm_var.get())
                except ValueError:
                    self._safe_msg("Invalid BPM", "Enter valid BPM.")
                    return

            if not self.bpm:
                self._safe_msg("Missing BPM", "Provide or detect BPM first.")
                return

            self.update_status(f"Using BPM: {self.bpm}")

            # ===============================
            # WHISPERX + OPTIONAL DEMUCS
            # ===============================

            if self.use_whisper_var.get():

                raw_lyrics = self.lyrics_box.get("1.0", tk.END).strip()

                try:
                    # ---- Decide whether to run Demucs ----
                    if "acapella" in self.audio_path.lower():
                        vocals_path = self.audio_path
                    else:
                        stems_dir = os.path.join(
                            os.path.dirname(self.audio_path),
                            "stems"
                        )
                        os.makedirs(stems_dir, exist_ok=True)

                        self.update_status("Separating vocals with Demucs...")
                        vocals_path = separate_vocals(
                            self.audio_path,
                            stems_dir
                        )

                except Exception as e:
                    self._safe_msg("Demucs Error", str(e))
                    return

                # ---- Run WhisperX ----
                self.update_status("Running WhisperX alignment...")

                try:
                    if raw_lyrics:
                        self.word_timestamps = transcribe_with_word_timestamps(
                            vocals_path,
                            lyrics=raw_lyrics
                        )
                    else:
                        self.word_timestamps = transcribe_with_word_timestamps(
                            vocals_path
                        )

                except Exception as e:
                    self._safe_msg("WhisperX Error", str(e))
                    return

                if not self.word_timestamps:
                    self._safe_msg(
                        "Alignment Error",
                        "No word timestamps generated."
                    )
                    return

            # =================================================
            # KEYWORDS
            # =================================================

            self.update_status("Extracting keywords...")

            model_name = self.model_var.get()
            openai_key = keyring.get_password(APP_NAME, "openai")
            gemini_key = keyring.get_password(APP_NAME, "gemini")

            lines = [
                l.strip()
                for l in self.lyrics_box.get("1.0", tk.END).split("\n")
                if l.strip()
            ]

            keywords = []

            if model_name.startswith("gpt"):
                if not openai_key:
                    self._safe_msg("Missing OpenAI Key", "Add your OpenAI key.")
                    return
                for line in lines:
                    keywords += extract_keywords(line, openai_key=openai_key)

            elif model_name.startswith("gemini"):
                if not gemini_key:
                    self._safe_msg("Missing Gemini Key", "Add your Gemini key.")
                    return
                for line in lines:
                    keywords += extract_keywords(line, gemini_key=gemini_key)

            if not keywords:
                keywords = [w["word"] for w in self.word_timestamps]

            # =================================================
            # VIDEO SEARCH
            # =================================================

            self.update_status("Searching stock videos...")

            searcher = VideoSearch(
                keyring.get_password(APP_NAME, "pexels"),
                keyring.get_password(APP_NAME, "pixabay"),
                resolution=self.resolution_var.get()
            )

            videos = searcher.search(keywords, per_query=6)

            if not videos:
                self._safe_msg("No Videos Found", "Try different keywords.")
                return

            # =================================================
            # TIMELINE
            # =================================================

            timeline = build_word_level_timeline(
                words=self.word_timestamps,
                bpm=self.bpm,
                subdivision=self.subdivision_var.get()
            )

            if not timeline:
                self._safe_msg("Timeline Error", "Timeline is empty.")
                return

            # =================================================
            # SAVE
            # =================================================

            save_path = filedialog.asksaveasfilename(
                defaultextension=".fcpxml",
                filetypes=[("Final Cut XML", "*.fcpxml")]
            )

            if not save_path:
                return

            media_dir = os.path.join(
                os.path.dirname(save_path),
                "media"
            )

            self.update_status("Downloading clips...")
            videos = searcher.download_videos(videos, media_dir)
            videos = [v for v in videos if v.get("local_path")]

            if not videos:
                self._safe_msg("Download Failed", "No videos downloaded.")
                return

            self.update_status("Exporting FCPXML...")

            export_fcpxml(
                videos=videos,
                timeline=timeline,
                resolution=self.resolution_var.get(),
                output_path=save_path
            )

            self._safe_msg("Success", f"Exported to:\n{save_path}")

        except Exception as e:
            self._safe_msg("Error", str(e))

        finally:
            self.update_status("Idle")

    # =====================================================
    # UI Helpers
    # =====================================================

    def _safe_msg(self, title, message):
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def update_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

        # =====================================================
        # Export subs
        # =====================================================       

    def export_subtitles(self):
        if not self.word_timestamps:
            self._safe_msg("Error", "No word timestamps available.")
            return

        if not self.bpm:
            self._safe_msg("Error", "BPM not set.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("Subtitle File", "*.srt")]
        )

        if not save_path:
            return

        export_srt(
            self.word_timestamps,
            self.bpm,
            self.subdivision_var.get(),
            save_path
        )

        self._safe_msg("Success", f"Subtitles exported:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricVisionApp(root)
    root.mainloop()