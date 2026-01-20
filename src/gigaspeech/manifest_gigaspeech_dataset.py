import os
import csv
import json
import soundfile as sf

# Thư mục chứa audio
audio_root = "/media/trandat/DataVoice/gigaspeech/data/audio/"

# Thư mục chứa CSV
csv_dir = "."

# Hàm lấy duration và sample_rate
def get_audio_info(wav_path):
    """
    Return duration (sec) and sample_rate
    """
    try:
        info = sf.info(wav_path)
        duration = info.frames / info.samplerate
        return round(duration, 3), info.samplerate
    except Exception as e:
        print(f"⚠️ Cannot read audio: {wav_path} ({e})")
        return None, None

# Lặp qua tất cả file CSV trong thư mục
for file_csv in ["dev_chunks_0000_metadata", "test_chunks_0000_metadata", "test_chunks_0001_metadata", "test_chunks_0002_metadata"]:
    csv_file = f"/media/trandat/DataVoice/gigaspeech/data/metadata/{file_csv}.csv"
    manifest_file = csv_file.replace("_metadata.csv", "_manifest.jsonl")
    print(f"Processing {csv_file} -> {manifest_file}")

    split = "dev_files" if "dev" in file_csv else "test_files"

    with open(csv_file, newline='', encoding='utf-8') as f_in, \
        open(manifest_file, "w", encoding='utf-8') as f_out:

        reader = csv.DictReader(f_in, delimiter=',')
        for row in reader:
            wav_path = os.path.join(audio_root, split, file_csv.replace('_metadata', ''), f"{row['sid']}.wav")
            if not os.path.exists(wav_path):
                print(f"Warning: {wav_path} không tồn tại, bỏ qua")
                continue
            duration, sample_rate = get_audio_info(wav_path)
            entry = {
                "file_id": row['aid'], 
                "file_path": os.path.join(split, file_csv.replace('_metadata', ''), f"{row['sid']}.wav"), 
                "duration": duration, 
                "sample_rate": sample_rate, 
                "start": row['begin_time'], 
                "end": row['end_time'], 
                "title": row['title'],
                "source": row["source"],
                "channels": int(row['channels']),
                "text": row['text_tn']
            }
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Tất cả manifest đã tạo xong ✅")

