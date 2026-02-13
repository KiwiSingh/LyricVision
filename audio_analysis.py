import librosa

def detect_bpm(audio_path):
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo)