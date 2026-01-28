import json


def _save_manifest(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def save_manifest(entry, path):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def save_file(outputs: str, manifests, output_name: str):
    MANIFEST_DIR = outputs / "manifests"
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    for split, entries in manifests.items():
        if not entries:
            continue

        out_path = MANIFEST_DIR / output_name.format(split)
        _save_manifest(entries, out_path)
        print(f"Saved {len(entries)} entries to {out_path}")