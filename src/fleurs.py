import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io, os
import numpy as np
from util.fillter_word_vi import check_text
from util.save_file import save_file
from util.process_row import process_row_with_file_audio


CSV_DIR = Path("/media/trandat/DataVoice/fleurs/data")
OUT_DIR = Path("/media/trandat/DataVoice/fleurs/output")

FILES_PER_DIR = 10000
csv_files = sorted(CSV_DIR.glob(f"*.tsv"))

manifests = {
    "vi": [],
    "cs": [],
}

audio_name = 0
for csv_file in tqdm(csv_files, desc="Process CSV"):
    print(f"Processing {csv_file.name}")
    df = pd.read_csv(csv_file, sep="\t")

    for _, row in df.iterrows():
        result = process_row_with_file_audio(row, audio_name, CSV_DIR / "audio" / csv_file.stem, df.columns)

        if result is None:
            continue

        fname = csv_file.name.lower()
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


save_file(OUT_DIR, manifests, "fleurs_{}.jsonl")

print("done")