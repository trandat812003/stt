import os
import csv
import json
import soundfile as sf

# Thư mục chứa audio
audio_root = "../audio"

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
for csv_file in os.listdir(csv_dir):
    if not csv_file.endswith(".csv"):
        continue
    
    manifest_file = csv_file.replace(".csv", "_manifest.jsonl")
    print(f"Processing {csv_file} -> {manifest_file}")

    with open(os.path.join(csv_dir, csv_file), newline='', encoding='utf-8') as f_in, \
         open(manifest_file, "w", encoding='utf-8') as f_out:

        reader = csv.DictReader(f_in, delimiter='|')
        for row in reader:
            wav_path = os.path.join(audio_root, row['wav_filename'])
            if not os.path.exists(wav_path):
                print(f"Warning: {wav_path} không tồn tại, bỏ qua")
                continue
            duration, sample_rate = get_audio_info(wav_path)
            entry = {
                "file_id": os.path.splitext(row['wav_filename'])[0], 
                "file_path": row['wav_filename'], 
                "duration": duration, 
                "sample_rate": sample_rate, 
                "transcript": row['transcript']
            }
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Tất cả manifest đã tạo xong ✅")
import os
import csv
import json
import soundfile as sf

# Thư mục chứa audio
audio_root = "../audio"

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
for csv_file in ["dev.csv","test.csv","train.csv"]:
    csv_file = f"/media/trandat/DataVoice/spgispeech/data/meta/{csv_file}"
    manifest_file = csv_file.replace(".csv", "_manifest.jsonl")
    print(f"Processing {csv_file} -> {manifest_file}")

    with open(os.path.join(csv_dir, csv_file), newline='', encoding='utf-8') as f_in, \
         open(manifest_file, "w", encoding='utf-8') as f_out:

        reader = csv.DictReader(f_in, delimiter='|')
        for row in reader:
            wav_path = os.path.join(audio_root, row['wav_filename'])
            if not os.path.exists(wav_path):
                print(f"Warning: {wav_path} không tồn tại, bỏ qua")
                continue
            duration, sample_rate = get_audio_info(wav_path)
            entry = {
                "file_id": os.path.splitext(row['wav_filename'])[0], 
                "file_path": row['wav_filename'], 
                "duration": duration, 
                "sample_rate": sample_rate, 
                "transcript": row['transcript']
            }
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Tất cả manifest đã tạo xong ✅")
