import os
import whisperx
import torch

MODEL_NAME = "large-v3"


def get_model_cache_dir():
    base = os.path.expanduser("~/Library/Application Support/LyricVision/models")
    os.makedirs(base, exist_ok=True)
    return base


def load_whisperx_model(device=None):

    # FORCE CPU — avoids MPS errors on macOS
    device = "cpu"

    model = whisperx.load_model(
        MODEL_NAME,
        device,
        compute_type="int8",  # best for CPU
        download_root=get_model_cache_dir()
    )

    return model, device


def transcribe_with_word_timestamps(audio_path, lyrics=None):
    """
    If lyrics is provided -> forced alignment using provided text.
    If lyrics is None -> normal transcription + alignment.
    """

    model, device = load_whisperx_model()
    audio = whisperx.load_audio(audio_path)

    # Always transcribe first (needed for language detection)
    result = model.transcribe(audio)

    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device
    )

    # -------------------------------------------------------
    # FORCED ALIGNMENT MODE
    # -------------------------------------------------------
    if lyrics:
        # Replace transcript segments with provided lyrics
        custom_segments = [{
            "text": lyrics.strip(),
            "start": 0,
            "end": result["segments"][-1]["end"] if result["segments"] else 0
        }]

        result_aligned = whisperx.align(
            custom_segments,
            model_a,
            metadata,
            audio,
            device
        )

    # -------------------------------------------------------
    # NORMAL TRANSCRIPTION MODE
    # -------------------------------------------------------
    else:
        result_aligned = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device
        )

    words = []

    for segment in result_aligned["segments"]:
        for word in segment.get("words", []):
            if "start" in word and "end" in word:
                words.append({
                    "word": word["word"],
                    "start": word["start"],
                    "end": word["end"]
                })

    return words