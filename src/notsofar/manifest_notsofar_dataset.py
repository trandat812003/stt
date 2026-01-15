import json, os
import soundfile as sf


ROOT_DIR = "/media/trandat/DataVoice/NOTSOFAR/benchmark-datasets/"


def get_audio_info(wav_path):
    try:
        info = sf.info(wav_path)
        return round(info.frames / info.samplerate, 3), info.samplerate
    except Exception as e:
        print(f"⚠️ Cannot read {wav_path}: {e}")
        return None, None


for split_dataset in os.listdir(ROOT_DIR):
    with open(f"./outputs/{split_dataset}.jsonl", "w", encoding='utf-8') as f_out:
        for vers in os.listdir(os.path.join(ROOT_DIR, split_dataset)):
            MTG_dir = os.path.join(ROOT_DIR, split_dataset, vers, "MTG")
            for mtg_folder in os.listdir(MTG_dir):
                with open(os.path.join(MTG_dir, mtg_folder, "gt_meeting_metadata.json"), "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                with open(os.path.join(MTG_dir, mtg_folder, "gt_transcription.json"), "r", encoding="utf-8") as f:
                    transcriptions = json.load(f)

                audio_file = {}
                for root, _, files in os.walk(f"{MTG_dir}/{mtg_folder}/close_talk"):
                    for f in files:
                        audio_file[f"close_talk/{f}"] = get_audio_info(f"{MTG_dir}/{mtg_folder}/close_talk/{f}")

                for data in transcriptions:
                    res = {
                        "file_id": data["ct_wav_file_name"], 
                        "file_path": f"{split_dataset}/{vers}/MTG/{mtg_folder}/{data['ct_wav_file_name']}", 
                        "duration": audio_file[data["ct_wav_file_name"]][0], 
                        "sample_rate": audio_file[data["ct_wav_file_name"]][1], 
                        "start": data["start_time"], 
                        "end": data["end_time"], 
                        "transcript": data["text"], 
                        "speaker": {
                            data["speaker_id"]: [
                                {"text": word_timing[0], "start": word_timing[1], "end": word_timing[2]} 
                                for word_timing in data["word_timing"]
                            ]
                        }
                    }
                    res = res | metadata
                    f_out.write(json.dumps(res, ensure_ascii=False) + "\n")

