# stt

```bassh
export HF_HOME=/tmp/ViMD && export HF_HUB_DISABLE_SYMLINKS=1 && hf download nguyendv02/ViMD_Dataset --repo-type dataset --local-dir /media/trandat/DataVoice/ViMD
```

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download speechcolab/gigaspeech --repo-type dataset --local-dir /media/trandat/DataVoice/gigaspeech --include "data/audio/xl_files_additional/xl_chunks_01*.tar.gz" 
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
mc mirror /media/trandat/DataVoice/gigaspeech/data/audio/ datnt/ic-smartvoice-vnpt-vn-viewer/asr/data/en/gigaspeech/data
```