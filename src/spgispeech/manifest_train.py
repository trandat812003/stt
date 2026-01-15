import os
import csv
import json
import tarfile
import shutil
import soundfile as sf
from tqdm import tqdm

# ================= CONFIG =================
AUDIO_ROOT = "/media/trandat/DataVoice/spgispeech/data/audio/train"
META_CSV = "/media/trandat/DataVoice/spgispeech/data/meta/train.csv"
OUT_MANIFEST_DIR = "./train_shards"
TMP_EXTRACT_DIR = "/tmp/spgispeech_train_extract"
# ========================================

os.makedirs(OUT_MANIFEST_DIR, exist_ok=True)
os.makedirs(TMP_EXTRACT_DIR, exist_ok=True)


def get_audio_info(wav_path):
    try:
        info = sf.info(wav_path)
        return round(info.frames / info.samplerate, 3), info.samplerate
    except Exception as e:
        print(f"⚠️ Cannot read {wav_path}: {e}")
        return None, None


# Load metadata CSV → dict lookup
meta_map = {}
with open(META_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        meta_map[row["wav_filename"]] = row["transcript"]

tar_files = sorted(f for f in os.listdir(AUDIO_ROOT) if f.endswith(".tar.gz"))
print(f"Found {len(tar_files)} tar files")

for tar_name in tqdm(tar_files, desc="Processing train tar files", unit="tar"):
    tar_path = os.path.join(AUDIO_ROOT, tar_name)

    # 👉 mỗi tar → 1 jsonl
    shard_name = tar_name.replace(".tar.gz", ".jsonl")
    shard_path = os.path.join(OUT_MANIFEST_DIR, shard_name)
    tqdm.write(f"📦 Processing {tar_name} → {shard_name}")

    tqdm.write(f"Extract {tar_name}")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(TMP_EXTRACT_DIR)

    tqdm.write(f"process {tar_name}")
    with open(shard_path, "w", encoding="utf-8") as fout:
        for root, _, files in os.walk(TMP_EXTRACT_DIR):
            for fn in files:
                check_file = os.path.basename(root) + "/" + fn
                if not fn.endswith(".wav"):
                    continue
                # breakpoint()
                if check_file not in meta_map:
                    continue

                wav_path = os.path.join(root, fn)
                duration, sr = get_audio_info(wav_path)
                if duration is None:
                    continue

                entry = {
                    "file_id": os.path.splitext(check_file)[0],
                    "file_path": f"train/{check_file}",   # chỉ lưu tên file
                    "duration": duration,
                    "sample_rate": sr,
                    "transcript": meta_map[check_file]
                }
                fout.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # breakpoint()

    # 3️⃣ Cleanup
    shutil.rmtree(TMP_EXTRACT_DIR)
    os.makedirs(TMP_EXTRACT_DIR, exist_ok=True)
    os.remove(tar_path)

    tqdm.write(f"✅ Done {tar_name}")

print("\n🎉 All train shards created successfully")
