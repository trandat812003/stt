import xml.etree.ElementTree as ET
import json
import os
import argparse
import glob

# =========================
# Constants
# =========================
NITE_URI = "http://nite.sourceforge.net/"
NITE_NS = {"nite": NITE_URI}


def speaker_to_headset(speaker):
    mapping = {
        "A": "Headset-0",
        "B": "Headset-1",
        "C": "Headset-2",
        "D": "Headset-3",
        "E": "Headset-4",
        "F": "Headset-5",
        "G": "Headset-6",
        "H": "Headset-7"
    }
    return mapping.get(speaker)


def parse_file_info(words_xml_path):
    base = os.path.basename(words_xml_path)
    parts = base.split(".")
    file_id = parts[0]
    speaker = parts[1]

    headset = speaker_to_headset(speaker)
    if headset is None:
        raise ValueError(f"Unknown speaker {speaker}")

    wav_path = os.path.join(
        f"{base.split('.')[0]}/audio/{base}",
        f"{file_id}.{headset}.wav"
    )

    return file_id, speaker, wav_path

# =========================
# Utils
# =========================
def parse_word_span(href):
    part = href.split("#id(")[1]
    if ")..id(" in part:
        start_id, end_id = part.split(")..id(")
        end_id = end_id.replace(")", "")
    else:
        start_id = part.replace(")", "")
        end_id = start_id
    return start_id, end_id


# =========================
# XML parsing
# =========================
def process_segments(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    segments = []
    # breakpoint()
    for seg in root.findall("segment"):
        child = seg.find("nite:child", NITE_NS)
        if child is None:
            continue

        start_w, end_w = parse_word_span(child.attrib["href"])

        segments.append({
            "segment_id": seg.attrib[f"{{{NITE_URI}}}id"],
            "start": float(seg.attrib["transcriber_start"]),
            "end": float(seg.attrib["transcriber_end"]),
            "start_w": start_w,
            "end_w": end_w
        })

    return segments


def process_words(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    words = []
    for w in root.findall("w"):
        if "starttime" not in w.attrib or "endtime" not in w.attrib:
            continue  # ← BỎ punctuation / token không time

        words.append({
            "id": w.attrib[f"{{{NITE_URI}}}id"],
            "text": w.text.strip() if w.text else "",
            "start": float(w.attrib["starttime"]),
            "end": float(w.attrib["endtime"])
        })

    return words


def collect_words(words, start_id, end_id):
    collected = []
    take = False
    for w in words:
        if w["id"] == start_id:
            take = True
        if take:
            collected.append(w)
        if w["id"] == end_id:
            break
    return collected


# =========================
# Metadata builder
# =========================
def build_metadata(segments, words, words_xml_path):
    file_id, speaker, wav_path = parse_file_info(words_xml_path)
    records = []

    for seg in segments:
        seg_words = collect_words(words, seg["start_w"], seg["end_w"])
        if not seg_words:
            continue

        records.append({
            "file_id": file_id,
            "file_path": wav_path,
            "duration": round(seg["end"] - seg["start"], 3),
            "sample_rate": 16000, 
            "segment_id": seg["segment_id"],
            "start": seg["start"],
            "end": seg["end"],
            "transcript": " ".join(w["text"] for w in seg_words),
            "speaker": {
                speaker: [
                    {
                        "text": w["text"],
                        "start": w["start"],
                        "end": w["end"]
                    }
                    for w in seg_words
                ]
            },
        })

    return records


# =========================
# Main directory processor
# =========================
def process_directory(words_dir, segments_dir, output_jsonl):
    all_records = []
    words_files = sorted(glob.glob(os.path.join(words_dir, "*.words.xml")))

    for words_xml in words_files:
        base = os.path.basename(words_xml)
        segments_xml = base.replace(".words.xml", ".segments.xml")
        segments_xml = os.path.join(segments_dir, segments_xml)

        if not os.path.exists(segments_xml):
            print(f"⚠️ Missing segments: {segments_xml}")
            continue

        segments = process_segments(segments_xml)
        words = process_words(words_xml)

        records = build_metadata(segments, words, words_xml)
        all_records.extend(records)

        print(f"✔ {base}: {len(records)} segments")

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n✅ TOTAL: {len(all_records)} segments written to {output_jsonl}")


# =========================
# CLI
# =========================
if __name__ == "__main__":
    # segments = process_segments("/media/trandat/DataVoice/AMI/ami_manual_1.6.1/segments/EN2002c.D.segments.xml")
    # words = process_words("/media/trandat/DataVoice/AMI/ami_manual_1.6.1/words/EN2002c.D.words.xml")
    # breakpoint()
    process_directory(
        "/media/trandat/DataVoice/AMI/ami_manual_1.6.1/words",
        "/media/trandat/DataVoice/AMI/ami_manual_1.6.1/segments",
        "ami_manifest.jsonl"
    )
