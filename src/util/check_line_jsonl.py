import json
from pathlib import Path
from fillter_word_vi import _check_text

CS_PATH = Path("/media/trandat/Data/viet_bud500/output/manifests/vietbud500_cs.jsonl")
TMP_PATH = Path("/media/trandat/Data/tmp.txt")

unique_words = set()

with open(CS_PATH, "r", encoding="utf-8") as fa:
    for line in fa:
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        text = obj.get("text", "")
        res = _check_text(text)

        for w in res:
            unique_words.add(w)

with open(TMP_PATH, "w", encoding="utf-8") as ftmp:
    for w in sorted(unique_words):
        ftmp.write(w + "\n")
