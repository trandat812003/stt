import os
import csv
import json
import tarfile
import shutil
import soundfile as sf
from tqdm import tqdm

# ================= CONFIG =================
AUDIO_ROOT = "/media/trandat/DataVoice/gigaspeech/data/audio/xl_files_additional"
OUT_MANIFEST_DIR = "./train_shards"
TMP_EXTRACT_DIR = "/tmp/gigaspeech_train_extract"
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
    csv_file = tar_path.replace("audio", "metadata").replace("files", "metadata").replace(".tar.gz","_metadata.csv")
    with open(csv_file, newline='', encoding='utf-8') as f_in, \
        open(shard_path, "w", encoding="utf-8") as fout:

        reader = csv.DictReader(f_in, delimiter=',')
        for row in reader:
            wav_path = os.path.join(TMP_EXTRACT_DIR, tar_name.replace(".tar.gz", ""), f"{row['sid']}.wav")
            if not os.path.exists(wav_path):
                print(f"Warning: {wav_path} không tồn tại, bỏ qua")
                continue
            duration, sample_rate = get_audio_info(wav_path)
            entry = {
                "file_id": row['aid'], 
                "file_path": os.path.join("xl_files_additional", tar_name.replace(".tar.gz", ""), f"{row['sid']}.wav"), 
                "duration": duration, 
                "sample_rate": sample_rate, 
                "start": row['begin_time'], 
                "end": row['end_time'], 
                "title": row['title'],
                "source": row["source"],
                "channels": int(row['channels']),
                "text": row['text_tn']
            }
            fout.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 3️⃣ Cleanup
    shutil.rmtree(TMP_EXTRACT_DIR)
    os.makedirs(TMP_EXTRACT_DIR, exist_ok=True)
    os.remove(tar_path)

    tqdm.write(f"✅ Done {tar_name}")

print("\n🎉 All train shards created successfully")
