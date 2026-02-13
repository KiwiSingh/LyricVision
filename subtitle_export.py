import math


def seconds_to_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def snap_to_grid(time, grid):
    return round(time / grid) * grid


def group_words_by_beat(words, bpm, subdivision="quarter"):
    seconds_per_beat = 60.0 / bpm

    if subdivision == "quarter":
        grid = seconds_per_beat
    elif subdivision == "eighth":
        grid = seconds_per_beat / 2
    elif subdivision == "sixteenth":
        grid = seconds_per_beat / 4
    else:
        grid = seconds_per_beat

    grouped = []
    current_line = []
    current_start = None

    for word in words:
        snapped_start = snap_to_grid(word["start"], grid)
        snapped_end = snap_to_grid(word["end"], grid)

        if current_start is None:
            current_start = snapped_start

        # If word crosses into new beat region → finalize previous line
        if snapped_start > current_start + grid:
            grouped.append({
                "start": current_start,
                "end": current_start + grid,
                "text": " ".join(current_line)
            })

            current_line = []
            current_start = snapped_start

        current_line.append(word["word"])

    # Flush last line
    if current_line:
        grouped.append({
            "start": current_start,
            "end": current_start + grid,
            "text": " ".join(current_line)
        })

    return grouped


def export_srt(words, bpm, subdivision, output_path):
    grouped = group_words_by_beat(words, bpm, subdivision)

    with open(output_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(grouped, start=1):
            start = seconds_to_srt_time(line["start"])
            end = seconds_to_srt_time(line["end"])

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{line['text'].strip()}\n\n")