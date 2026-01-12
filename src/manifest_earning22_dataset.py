import os
import csv
import json

media_dir = "/media/trandat/DataVoice/speech-datasets/earnings22/media"
nlp_dir   = "/media/trandat/DataVoice/speech-datasets/earnings22/transcripts/force_aligned_nlp_references"

meta_file = "/media/trandat/DataVoice/speech-datasets/earnings22/metadata.csv"

output_jsonl = "earnings22_manifest.jsonl"

# --- load file metadata ---
file_meta = {}
with open(meta_file, newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        # breakpoint()
        file_meta[r["File ID"]] = {
            "duration": float(r["File Length (seconds)"]),
            "sample_rate": int(r["Sampling Rate (Hz)"]),
            "UN Defined": r["UN Defined"],
            "Country by Ticker": r["Country by Ticker"],
            "Major Dialect Family": r["Major Dialect Family"],
            "Language Family + Area Based": r["Language Family + Area Based"],
            "Ticker Symbol": r["Ticker Symbol"]
        }


# --- create JSONL ---
with open(output_jsonl, "w", encoding="utf-8") as fout:

    for nlp_file in sorted(os.listdir(nlp_dir)):
        if not nlp_file.endswith(".nlp"):
            continue

        file_id = os.path.splitext(nlp_file)[0].replace(".aligned", "")
        mp3_file = os.path.join(media_dir, f"{file_id}.mp3")
        # breakpoint()
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
                if len(parts) < 8:
                    continue

                token, speaker_id, ts, endTs, punct, prepunct, case, tags = parts[:8]

                # determine speaker name or fallback
                speaker_name = f"speaker_{speaker_id}"

                # combine token + punctuation
                token = (prepunct if prepunct else "") + token
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
            "UN Defined": meta.get("UN Defined"),
            "Country by Ticker": meta.get("Country by Ticker"),
            "Major Dialect Family": meta.get("Major Dialect Family"),
            "Ticker Symbol": meta.get("Ticker Symbol"),
            "transcript": full_transcript,
            "speakers": speaker_output
        }

        # write one JSON per line
        fout.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Done! JSONL with timestamps:", output_jsonl)
