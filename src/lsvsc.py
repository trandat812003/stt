import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io, os
from util.fillter_word_vi import check_text


PARQUET_DIR = Path("/media/trandat/DataVoice/LSVSC/data")
OUT_DIR = Path("output")

AUDIO_DIR = OUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

parquet_files = sorted(PARQUET_DIR.glob(f"*.parquet"))

manifests = {
    "train": [],
    "test": [],
    "validate": [],
    "cs": [],
}

audio_name = 0
for parquet_file in tqdm(parquet_files, desc="Process parquet"):
    print(f"Processing {parquet_file.name}")
    df = pd.read_parquet(parquet_file)

    for _, row in df.iterrows():
        text = row["transcription"]
        audio = row["audio"]

        if isinstance(audio, dict):
            wav_bytes = audio["bytes"]
        elif isinstance(audio, (bytes, bytearray)):
            wav_bytes = audio
        else:
            raise TypeError(f"Unknown audio type: {type(audio)}")
        
        waveform, sr = sf.read(io.BytesIO(wav_bytes))

        audio_path = f"{AUDIO_DIR}/{audio_name}.wav"
        sf.write(audio_path, waveform, sr)

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
            "file_id": audio_name,
            "file_path": f"{audio_name}.wav",
            "text": text,
            "sample_rate": sr,
        })
        if check_text(text):
            manifests[split].append(entry)
        else:
            entry["split"] = split
            manifests["cs"].append(entry)

        audio_name += 1


def save_manifest(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


MANIFEST_DIR = OUT_DIR / "manifests"
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
for split, entries in manifests.items():
    if not entries:
        continue

    out_path = MANIFEST_DIR / f"lsvsc_{split}.jsonl"
    save_manifest(entries, out_path)
    print(f"Saved {len(entries)} entries to {out_path}")

print("done")