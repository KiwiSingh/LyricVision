def snap_to_grid(time, grid):
    return round(time / grid) * grid


def build_word_level_timeline(words, bpm, subdivision="quarter"):
    if not words:
        return []

    seconds_per_beat = 60.0 / bpm

    if subdivision == "quarter":
        grid = seconds_per_beat
    elif subdivision == "eighth":
        grid = seconds_per_beat / 2
    elif subdivision == "sixteenth":
        grid = seconds_per_beat / 4
    else:
        grid = seconds_per_beat

    # Sort words by start time
    words = sorted(words, key=lambda w: w["start"])

    timeline = []

    for i, word in enumerate(words):
        snapped_start = snap_to_grid(word["start"], grid)

        # Determine next boundary
        if i < len(words) - 1:
            next_start = snap_to_grid(words[i + 1]["start"], grid)
            duration = max(grid, next_start - snapped_start)
        else:
            duration = grid

        timeline.append({
            "text": word["word"],
            "start": snapped_start,
            "duration": duration,
            "end": snapped_start + duration
        })

    return timeline