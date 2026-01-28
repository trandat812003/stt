import pandas as pd
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io
import numpy as np
import pyarrow.parquet as pq
import gc

from util.fillter_word_vi import check_text
from util.save_file import save_manifest


PARQUET_DIR = Path("/media/trandat/DataVoice/VietSpeech/data")
OUT_DIR = Path("/media/trandat/Data/VietSpeech/output")

AUDIO_DIR = OUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

FILES_PER_DIR = 10000
BATCH_SIZE = 128   # 🔥 chỉnh 64–256 tùy RAM

parquet_files = sorted(PARQUET_DIR.glob("*.parquet"))


def process_row(row, audio_id: int):
    # ---- lấy text ----
    text = (
        row.get("transcription")
        or row.get("text")
        or row.get("label")
        or row.get("transcript")
    )
    if not text:
        return None

    audio = row["audio"]

    if isinstance(audio, dict):
        wav_bytes = audio["bytes"]
        audio_path = audio.get("path") or f"{audio_id}.wav"
    elif isinstance(audio, (bytes, bytearray)):
        wav_bytes = audio
        audio_path = f"{audio_id}.wav"
    else:
        return None

    # ---- đọc audio ----
    try:
        waveform, sr = sf.read(io.BytesIO(wav_bytes))
    except Exception:
        return None

    if waveform is None or len(waveform) == 0:
        return None

    if not np.isfinite(waveform).all():
        return None

    # ---- ghi file ----
    subdir = f"{audio_id // FILES_PER_DIR:05d}"
    audio_subdir = AUDIO_DIR / subdir
    audio_subdir.mkdir(parents=True, exist_ok=True)

    sf.write(audio_subdir / audio_path, waveform, sr)

    # ---- cleanup ----
    del waveform
    del wav_bytes

    return text, f"{subdir}/{audio_path}", audio_id + 1


audio_id = 0

for parquet_file in tqdm(parquet_files, desc="Process parquet"):
    print(f"Processing {parquet_file.name}")
    base_name = parquet_file.stem
    fname = parquet_file.name.lower()

    if "train" in fname:
        split = "train"
    elif "test" in fname:
        split = "test"
    else:
        split = "validate"

    pf = pq.ParquetFile(parquet_file)

    for batch in pf.iter_batches(batch_size=BATCH_SIZE):
        df = batch.to_pandas()

        for row in df.to_dict(orient="records"):
            result = process_row(row, audio_id)
            if result is None:
                continue

            text, file_path, audio_id = result

            entry = {
                "file_path": file_path,
                "text": text,
            }

            if check_text(text):
                save_manifest(entry, f"vietspeech_{base_name}_vi.jsonl")
            else:
                save_manifest(entry, f"vietspeech_{base_name}_cs.jsonl")

        # 🔥 batch cleanup
        del df
        gc.collect()

    # 🔥 xóa parquet sau khi xong
    parquet_file.unlink()

print("done")
