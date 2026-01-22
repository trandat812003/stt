import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io, os
import numpy as np
from util.fillter_word_vi import check_text


PARQUET_DIR = Path("/media/trandat/DataVoice/viet_bud500/data")
OUT_DIR = Path("/media/trandat/Data/viet_bud500/output")

AUDIO_DIR = OUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

parquet_files = sorted(PARQUET_DIR.glob(f"*.parquet"))
FILES_PER_DIR = 10000

manifests = {
    "vi": [],
    "cs": [],
}

audio_name = 0
for parquet_file in tqdm(parquet_files, desc="Process parquet"):
    print(f"Processing {parquet_file.name}")
    df = pd.read_parquet(parquet_file)

    for _, row in df.iterrows():
        text = row["transcription"]
        audio = row["audio"]
        # breakpoint()

        if isinstance(audio, dict):
            wav_bytes = audio["bytes"]
            audio_path = audio["path"]
            if audio_path is None:
                audio_path = f"{audio_name}.wav"
        elif isinstance(audio, (bytes, bytearray)):
            wav_bytes = audio
            audio_path = f"{audio_name}.wav"
        else:
            raise TypeError(f"Unknown audio type: {type(audio)}")
        
        waveform, sr = sf.read(io.BytesIO(wav_bytes))

        if waveform is None or len(waveform) == 0:
            continue

        if np.isnan(waveform).any():
            continue

        subdir = f"{audio_name // FILES_PER_DIR:05d}"
        audio_subdir = AUDIO_DIR / subdir
        audio_subdir.mkdir(parents=True, exist_ok=True)

        sf.write(audio_subdir / audio_path, waveform, sr)

        if waveform.ndim == 1:
            num_samples = waveform.shape[0]
        else:
            num_samples = waveform.shape[0]

        duration = num_samples / sr

        fname = parquet_file.name.lower()
        if "train" in fname:
            split = "train"
        elif "test" in fname:
            split = "test"
        else:
            split = "validate"

        entry = {}
        for col in df.columns:
            if col == "audio":
                continue
            if col == "transcription":
                continue
            entry[col] = row[col]

        entry.update({
            "file_id": os.path.splitext(audio_path)[0],
            "file_path": f"{subdir}/{audio_path}",
            "text": text,
            "sample_rate": sr,
            "duration": duration,
            "split": split,
        })
        if check_text(text):
            manifests["vi"].append(entry)
        else:
            manifests["cs"].append(entry)

        audio_name = audio_name + 1


def save_manifest(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


MANIFEST_DIR = OUT_DIR / "manifests"
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
for split, entries in manifests.items():
    if not entries:
        continue

    out_path = MANIFEST_DIR / f"vietbud500_{split}.jsonl"
    save_manifest(entries, out_path)
    print(f"Saved {len(entries)} entries to {out_path}")

print("done")