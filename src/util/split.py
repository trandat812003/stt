import json
from pathlib import Path
from fillter_word_vi import check_text


CS_PATH = Path("/media/trandat/Data/LSVSC/output/manifests/lsvsc_cs.jsonl")
TMP_PATH = Path("/media/trandat/Data/LSVSC/output/manifests/lsvsc.tmp.jsonl")
VI_PATH = Path("/media/trandat/Data/LSVSC/output/manifests/lsvsc_vi.jsonl")

moved = 0
kept = 0

with open(CS_PATH, "r", encoding="utf-8") as fa, \
        open(TMP_PATH, "w", encoding="utf-8") as ftmp, \
        open(VI_PATH, "a", encoding="utf-8") as fvi:

    for line in fa:
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            ftmp.write(line + "\n")
            kept += 1
            continue

        text = obj.get("text", "")
        
        if check_text(text):
            fvi.write(line + "\n")
            moved += 1
        else:
            ftmp.write(line + "\n")
            kept += 1


CS_PATH.unlink()
TMP_PATH.rename(CS_PATH)

print(f"Moved  : {moved}")
print(f"Kept   : {kept}")