import soundfile as sf
import io, os
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

FILES_PER_DIR = 10000


def process_row(row: Dict[str, Any], audio_id: int, audio_dir: Path, columns: List) -> Optional[dict]:
    text = None
    if "transcription" in row and row["transcription"]:
        text = row["transcription"]
    elif "text" in row and row["text"]:
        text = row["text"]
    elif "label" in row and row["label"]:
        text = row["label"]
    elif "transcript" in row and row["transcript"]:
        text = row["transcript"]

    if text is None:
        return None
    audio = row["audio"]
    # breakpoint()

    if isinstance(audio, dict):
        wav_bytes = audio["bytes"]
        audio_path = audio["path"]
        if audio_path is None:
            audio_path = f"{audio_id}.wav"
    elif isinstance(audio, (bytes, bytearray)):
        wav_bytes = audio
        audio_path = f"{audio_id}.wav"
    else:
        raise TypeError(f"Unknown audio type: {type(audio)}")
    
    waveform, sr = sf.read(io.BytesIO(wav_bytes))

    if waveform is None or len(waveform) == 0 or np.isnan(waveform).any():
        return None

    subdir = f"{audio_id // FILES_PER_DIR:05d}"
    audio_subdir = audio_dir / subdir
    audio_subdir.mkdir(parents=True, exist_ok=True)

    sf.write(audio_subdir / audio_path, waveform, sr)

    if waveform.ndim == 1:
        num_samples = waveform.shape[0]
    else:
        num_samples = waveform.shape[0]

    duration = num_samples / sr

    entry = {}
    for col in columns:
        if col in ["audio", "text", "translation", "language", "transcription", "label", "transcript", "file_name"]:
            continue
        entry[col] = row[col]

    audio_id += 1

    return entry, text, os.path.splitext(audio_path)[0], f"{subdir}/{audio_path}", audio_id, duration, sr


def process_row_with_file_audio(row: Dict[str, Any], audio_id: int, audio_dir: Path, columns: List) -> Optional[dict]:
    text = None
    if "transcription" in row and row["transcription"]:
        text = row["transcription"]
    elif "text" in row and row["text"]:
        text = row["text"]
    elif "label" in row and row["label"]:
        text = row["label"]
    elif "transcript" in row and row["transcript"]:
        text = row["transcript"]

    if text is None:
        return None
    
    if "file_name" in row and row["file_name"]:
        audio_path = row["file_name"]
    elif "file_path" in row and row["file_path"]:
        audio_path = row["file_path"]

    try:
        with sf.SoundFile(os.path.join(audio_dir, audio_path)) as f:
            sr = f.samplerate
            frames = len(f)
            duration = frames / sr
    except Exception as e:
        print(f"[WARN] Cannot read audio {audio_path}: {e}")
        return None

    entry = {}
    for col in columns:
        if col in ["audio", "text", "translation", "language", "transcription", "label", "transcript", "file_name"]:
            continue
        entry[col] = row[col]

    audio_id += 1

    return entry, text, os.path.splitext(audio_path)[0], f"{audio_dir.name}/{audio_path}", audio_id, duration, sr