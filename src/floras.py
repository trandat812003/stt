import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io, os
import numpy as np
from util.fillter_word_vi import check_text
from util.save_file import save_file
from util.process_row import process_row



PARQUET_DIR = Path("/media/trandat/DataVoice/floras/multilingual")
OUT_DIR = Path("/media/trandat/Data/floras/output")

AUDIO_DIR = OUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
FILES_PER_DIR = 10000

parquet_files = sorted(PARQUET_DIR.glob(f"*.parquet"))

manifests = {
    "vi": [],
    "cs": [],
}

audio_name = 0
for parquet_file in tqdm(parquet_files, desc="Process parquet"):
    print(f"Processing {parquet_file.name}")
    df = pd.read_parquet(parquet_file)

    for _, row in df.iterrows():
        lang = row["language"]

        if lang != 'vi': 
            continue

        result = process_row(row, audio_name, AUDIO_DIR, df.columns)

        if result is None:
            continue

        fname = parquet_file.name.lower()
        if "train" in fname:
            split = "train"
        elif "test" in fname:
            split = "test"
        else:
            split = "validate"

        entry, text, file_id, file_path, audio_name, duration, sr = result

        entry.update({
            "file_id": file_id,
            "file_path": file_path,
            "text": text,
            "sample_rate": sr,
            "duration": duration,
            "split": split,
        })
        if check_text(text):
            manifests["vi"].append(entry)
        else:
            manifests["cs"].append(entry)


save_file(OUT_DIR, manifests, f"floras_{split}.jsonl")

print("done")