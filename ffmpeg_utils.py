import subprocess
import os
import tempfile
import sys

def get_ffmpeg_path():
    """
    Returns bundled ffmpeg path if running in PyInstaller,
    otherwise assumes ffmpeg is in PATH.
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg")
    return "ffmpeg"

def convert_to_wav(input_path):
    """
    Converts any audio format to 44.1kHz WAV using ffmpeg.
    Returns path to temp WAV file.
    """
    ffmpeg = get_ffmpeg_path()
    temp_wav = tempfile.mktemp(suffix=".wav")

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-ar", "44100",
        "-ac", "2",
        temp_wav
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return temp_wav

def extract_audio_from_video(video_path):
    """
    Extracts audio track from video.
    """
    ffmpeg = get_ffmpeg_path()
    temp_wav = tempfile.mktemp(suffix=".wav")

    command = [
        ffmpeg,
        "-y",
        "-i", video_path,
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        temp_wav
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return temp_wav