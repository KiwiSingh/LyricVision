# LyricVision 🎬🎵

<p align="center">
  <a href="https://ibb.co/SwcN4w7p">
    <img src="https://i.ibb.co/HTC7fTpQ/E86-FD729-4-E1-F-434-C-A300-F659824-EE687.png" alt="LyricVision Logo" width="400">
  </a>
</p>

**LyricVision** is an AI-assisted music video planning tool that
converts lyrics into beat-snapped timelines, automatically sources stock
footage, and exports fully structured FCPXML files for professional
editing in DaVinci Resolve and Final Cut Pro.

It bridges songwriting and video production --- turning words into
visual structure.

------------------------------------------------------------------------

## ✨ Features

-   🎙 WhisperX Word-Level Alignment
-   🎚 Optional Demucs Vocal Separation
-   🧠 AI Keyword Extraction (OpenAI / Gemini)
-   🎥 Stock Footage Integration (Pexels / Pixabay)
-   🥁 Beat-Snapped Timeline Builder (Quarter / Eighth / Sixteenth)
-   📂 Automatic Clip Download + Media Folder Creation
-   🎬 FCPXML Export (Resolve & Final Cut compatible)
-   🔐 Secure API key storage via system keyring

------------------------------------------------------------------------

## 🛠 Installation

### 🖥 Option A --- Run from Source

``` bash
git clone https://github.com/YOUR_USERNAME/LyricVision.git
cd LyricVision

conda create -n lyricvision python=3.12
conda activate lyricvision

pip install -r requirements.txt
python lyricvision_app.py
```

------------------------------------------------------------------------

### 💿 Option B --- macOS Packaged App (DMG)

1.  Download the latest `.dmg` from the **Releases** section.
2.  Double-click the DMG to mount it.
3.  Drag **LyricVision.app** into your Applications folder (or anywhere
    you prefer).
4.  If macOS blocks it, run:

``` bash
sudo xattr -rd com.apple.quarantine /Applications/LyricVision.app
```

Or if running directly from mounted volume:

``` bash
sudo xattr -rd com.apple.quarantine /Volumes/LyricVision/LyricVision.app
```

Then launch normally.

------------------------------------------------------------------------

## 🔑 API Keys

LyricVision supports:

-   OpenAI
-   Google Gemini
-   Pexels
-   Pixabay

Use the built-in **Manage API Keys** window to securely store keys.

------------------------------------------------------------------------

## 🎬 Importing into DaVinci Resolve

1.  Open Resolve
2.  Go to **File → Import Timeline → Import FCPXML**
3.  Select exported file
4.  Ensure resolution matches export
5.  Relink media if prompted

------------------------------------------------------------------------

## 📱 Vertical Version Workflow

Duplicate timeline → change resolution to 9:16 → use Smart Reframe or
manual transforms.
Subtitles and Text+ workflows supported.


------------------------------------------------------------------------

## 📜 License

LyricVision is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

This project bundles a GPL-enabled build of FFmpeg.
As required by the GPL, LyricVision is distributed under the same license.

See the LICENSE file for full details.

## 📜 Third-Party Software

### FFmpeg

LyricVision bundles FFmpeg, a free and open-source multimedia framework.

- Website: https://ffmpeg.org  
- Source Code: https://github.com/FFmpeg/FFmpeg  
- License: GNU General Public License (GPL) v3 or later  
- License Text: See THIRD_PARTY_LICENSES/GPL-3.0.txt  

This build of FFmpeg was compiled with GPL-enabled components (`--enable-gpl`).

Because of this, LyricVision is distributed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

In compliance with the GPL:

- The complete corresponding source code for FFmpeg is available from the official FFmpeg repository linked above.
- LyricVision’s full source code is publicly available.
- You may modify and redistribute LyricVision under the terms of the GPL.

Note: FFmpeg is not affiliated with LyricVision.
FFmpeg is developed by the FFmpeg project contributors.

------------------------------------------------------------------------

## ☕ Support the Project

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/kiwisingh)

------------------------------------------------------------------------

## 🌐 Creator

Made by Kiwi Singh
🔗 https://char1ot33r.com
