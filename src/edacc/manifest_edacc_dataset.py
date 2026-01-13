import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
import soundfile as sf
import io, os

PARQUET_DIR = Path("/media/trandat/DataVoice/edacc/data")
OUT_DIR = Path("output")

AUDIO_DIR = OUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SPLITS = ["validation", "test"]

# tạo thư mục audio theo split
for split in SPLITS:
    (AUDIO_DIR / split).mkdir(exist_ok=True)

manifests = {
    "validation": [],
    "test": []
}

global_idx = {
    "validation": 0,
    "test": 0
}

# duyệt theo từng split
for split in SPLITS:
    parquet_files = sorted(PARQUET_DIR.glob(f"{split}-*.parquet"))
    print(f"{split}: {len(parquet_files)} parquet files")

    for parquet_file in parquet_files:
        print(f"Processing {parquet_file.name}")
        df = pd.read_parquet(parquet_file)

        for _, row in tqdm(df.iterrows(), total=len(df)):
            audio = row["audio"]

            if isinstance(audio, dict):
                wav_bytes = audio["bytes"]
                audio_name = audio["path"]
            elif isinstance(audio, (bytes, bytearray)):
                wav_bytes = audio
                audio_name = f"{split}_{global_idx[split]}.wav"
            else:
                raise TypeError(f"Unknown audio type: {type(audio)}")

            # audio_path = AUDIO_DIR / split / audio_name

            waveform, sr = sf.read(io.BytesIO(wav_bytes))

            # with open(audio_path, "wb") as f:
            #     sf.write(audio_path, waveform, sr)

            manifests[split].append({
                "file_id": os.path.splitext(audio_name)[0],
                "file_path": f"{split}/{os.path.basename(audio_name)}",
                "transcript": row["text"],
                "sample_rate": sr,
                "speakers": row["speaker"],
                "accent": row["accent"],
                "raw_accent": row["raw_accent"],
                "gender": row["gender"],
                "l1": row["l1"],
            })

            global_idx[split] += 1

# lưu manifest theo split
for split in SPLITS:
    manifest_path = OUT_DIR / f"{split}_edacc_manifest.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for r in manifests[split]:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("Done")
