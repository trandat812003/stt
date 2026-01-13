# stt

```bassh
export HF_HUB_DISABLE_SYMLINKS=1 && hf download edinburghcstr/edacc --repo-type dataset --local-dir /media/trandat/DataVoice/edacc
```

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download facebook/voxpopuli --repo-type dataset --local-dir /media/trandat/DataVoice/voxpopuli --include "data/en_accented/**"
```

```bash
export HF_HUB_DISABLE_SYMLINKS=1 && hf download speechcolab/gigaspeech --repo-type dataset --local-dir /media/trandat/DataVoice/gigaspeech --exclude "data/audio/xl_files_additional/**"
```

```bash
find . -type f -name "*.tar.gz" -exec tar -xzf {} \;
```
