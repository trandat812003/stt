import os
import csv
import json

media_dir = "/media/trandat/DataVoice/speech-datasets/earnings21/media"
nlp_dir   = "/media/trandat/DataVoice/speech-datasets/earnings21/transcripts/nlp_references"

meta_file = "/media/trandat/DataVoice/speech-datasets/earnings21/earnings21-file-metadata.csv"
speaker_meta_file = "/media/trandat/DataVoice/speech-datasets/earnings21/speaker-metadata.csv"

output_jsonl = "../../manifest/earnings21_manifest.jsonl"

# --- load file metadata ---
file_meta = {}
with open(meta_file, newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        file_meta[r["file_id"]] = {
            "duration": float(r["audio_length"]),
            "sample_rate": int(r["sample_rate"]),
            "company_name": r["company_name"],
            "financial_quarter": r["financial_quarter"],
            "sector": r["sector"]
        }

# --- load speaker id -> name ---
speaker_map = {}
with open(speaker_meta_file, newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        key = (r["file_id"], r["speaker_id"])
        speaker_map[key] = r["speaker_name"]

# --- create JSONL ---
with open(output_jsonl, "w", encoding="utf-8") as fout:

    for nlp_file in sorted(os.listdir(nlp_dir)):
        if not nlp_file.endswith(".nlp"):
            continue

        file_id = os.path.splitext(nlp_file)[0]
        mp3_file = os.path.join(media_dir, f"{file_id}.mp3")
        if not os.path.exists(mp3_file):
            continue
        mp3_file = os.path.basename(mp3_file)

        # build per-speaker lists
        speakers_dict = {}
        full_transcript_tokens = []

        with open(os.path.join(nlp_dir, nlp_file), encoding="utf-8") as f:
            next(f)   # skip header if needed
            for line in f:
                parts = line.strip().split("|")
                # ensure correct columns
                if len(parts) < 7:
                    continue

                token, speaker_id, ts, endTs, punct, case, tags = parts[:7]

                # determine speaker name or fallback
                speaker_name = speaker_map.get(
                    (file_id, speaker_id),
                    f"speaker_{speaker_id}"
                )

                # combine token + punctuation
                word = token + (punct if punct else "")

                # add to full sequence
                full_transcript_tokens.append(word)

                # parse timing, fallback to None if empty
                try:
                    start = float(ts)   if ts   else None
                    stop  = float(endTs) if endTs else None
                except:
                    start, stop = None, None

                # add into speaker dict
                if speaker_name not in speakers_dict:
                    speakers_dict[speaker_name] = []

                speakers_dict[speaker_name].append({
                    "token": word,
                    "ts": start,
                    "endTs": stop
                })

        # build full transcript string
        full_transcript = " ".join(full_transcript_tokens)

        # join speaker data
        # now each speaker is a list of token objects
        speaker_output = speakers_dict

        meta = file_meta.get(file_id, {})

        record = {
            "file_id": file_id,
            "file_path": mp3_file,
            "duration": meta.get("duration"),
            "sample_rate": meta.get("sample_rate"),
            "company_name": meta.get("company_name"),
            "financial_quarter": meta.get("financial_quarter"),
            "sector": meta.get("sector"),
            "transcript": full_transcript,
            "speakers": speaker_output
        }

        # write one JSON per line
        fout.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Done! JSONL with timestamps:", output_jsonl)
