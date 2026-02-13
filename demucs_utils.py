import os
import subprocess


def separate_stems(audio_path, output_dir):
    """
    Runs Demucs to separate stems into the given output directory.
    Returns the folder containing separated stems.
    """

    os.makedirs(output_dir, exist_ok=True)

    command = [
        "demucs",
        "-n", "htdemucs",
        "--two-stems=vocals",
        "-o", output_dir,
        audio_path
    ]

    subprocess.run(command, check=True)

    # Demucs creates:
    # output_dir/htdemucs/<filename_without_ext>/
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    stems_path = os.path.join(output_dir, "htdemucs", base_name)

    return stems_path


def separate_vocals(audio_path, output_dir):
    """
    Returns path to isolated vocals file.
    """

    stems_path = separate_stems(audio_path, output_dir)

    vocals_path = os.path.join(stems_path, "vocals.wav")

    if not os.path.exists(vocals_path):
        raise FileNotFoundError("Vocals file not found after Demucs separation.")

    return vocals_path