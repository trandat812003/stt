import csv
import json
import os
import argparse
import soundfile as sf

def read_tsv(tsv_path):
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)
    

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


def build_manifest(tsv_path, audio_root, output_jsonl):
    rows = read_tsv(tsv_path)
    records = []

    for r in rows:
        wav_path = os.path.join(
            audio_root,
            r["split"],
            f"{r['id']}.wav"
        )

        if not os.path.exists(wav_path):
            # VoxPopuli có vài file thiếu → skip
            continue

        duration, sample_rate = get_audio_info(wav_path)
        if duration is None:
            continue

        record = {
            "file_id": r["id"],
            "file_path": f"{r['split']}/{r['id']}.wav",
            "duration": duration, 
            "sample_rate": sample_rate, 
            "transcript": r["raw_text"],
            "speaker_id": r["speaker_id"],
            "gender": r["gender"],
            "accent": r.get("accent"),
        }

        records.append(record)

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ {output_jsonl}: {len(records)} samples")


def process_language(root_dir, language):
    for split in ["train", "dev", "test"]:
        tsv = os.path.join(root_dir, f"asr_{split}.tsv")
        if not os.path.exists(tsv):
            continue

        build_manifest(
            tsv_path=tsv,
            audio_root=root_dir,
            output_jsonl=f"voxpopuli_{language}_{split}.jsonl"
        )


if __name__ == "__main__":
    data_root = "/media/trandat/DataVoice/voxpopuli/data"

    # process_language(os.path.join(data_root, "en"), "en")
    process_language(os.path.join(data_root, "en"), "en")
