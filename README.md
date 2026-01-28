# stt

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download UIT-ViToSA/ViToSA-1.0 --repo-type dataset --local-dir /media/trandat/DataVoice/ViToSA
```

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download google/fleurs --repo-type dataset --local-dir /media/trandat/DataVoice/fleurs --include "data/vi_vn/**" 
```

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download speechcolab/gigaspeech --repo-type dataset --local-dir /media/trandat/DataVoice/gigaspeech --exclude "data/audio/**"
```

```bash
find . -type f -name "*.tar.gz" -exec tar -xzf {} \;
```

```bash
find . -type f -name "*.tar.gz" -exec sh -c '
  for f; do
    tar -xzf "$f" -C "$(dirname "$f")" && rm -rf "$f"
  done
' sh {} +
```

```bash
cat *.jsonl > all.jsonl
```

```bash
mc mirror /media/trandat/DataVoice/opus/train_files datnt/ic-smartvoice-vnpt-vn-viewer/asr/data/en/gigaspeech/data/opus/xl_files_additional

mc rm --recursive --force datnt/ic-smartvoice-vnpt-vn-viewer/asr/data/vi/fpt_fosd

mc find datnt/ic-smartvoice-vnpt-vn-viewer/asr/data/en/gigaspeech/data/wav/audio/xl_files_additional \
  --name "xl_chunks_00*.tar.gz" \
  --exec "mc cp {} /media/trandat/DataVoice/gigaspeech/train_files/"
```

```bash
jq -c '{file_path, text}' input.jsonl > output.mono_language.jsonl
```
