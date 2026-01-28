#!/usr/bin/env bash
set -e

P=viet_bud500

SRC_DIR=/media/trandat/DataVoice/${P}/

TMP_DIR=/tmp/${P}_extract
TMP_OPUS=/media/trandat/DataVoice/${P}/opus/
TMP_WAV=/media/trandat/DataVoice/${P}/wav/

DST=/media/trandat/DataVoice/${P}/

BITRATE=32k
SR=16000
JOBS=8

# mkdir -p "$TMP_DIR" "$TMP_OPUS" "$TMP_WAV" "$DST" 
# find "$SRC_DIR" -type f \( \
#   -name "*.zip" -o \
#   -name "*.tar" -o \
#   -name "*.tar.gz" -o \
#   -name "*.tgz" -o \
#   -name "*.rar" \
# \) -print0 | while IFS= read -r -d '' f; do
#   echo "Extracting: $f"

#   case "$f" in
#     *.zip)
#       unzip -oq "$f" -d "$TMP_DIR"
#       ;;
#     *.tar)
#       tar -xf "$f" -C "$TMP_DIR"
#       ;;
#     *.tar.gz|*.tgz)
#       tar -xzf "$f" -C "$TMP_DIR"
#       ;;
#     *.rar)
#       unrar x -o+ "$f" "$TMP_DIR" >/dev/null
#       ;;
#   esac
# done
echo "convert."
TMP_DIR=$TMP_DIR/audio
find "$TMP_DIR" -type f -name "*.wav" -print0 | \
xargs -0 -n 1 -P "$JOBS" bash -c '
  f="$0"

  # path tương đối trong /tmp
  rel="${f#"'$TMP_DIR'/"}"
  rel="${rel#audio/}"

  out_opus="'$TMP_OPUS'/${rel%.wav}.opus"
  out_wav="'$TMP_WAV'/${rel%.wav}.wav"

  mkdir -p "$(dirname "$out_opus")" "$(dirname "$out_wav")"

  # WAV -> OPUS
  ffmpeg -y -loglevel error \
    -i "$f" \
    -ac 1 -ar '"$SR"' \
    -c:a libopus -b:a '"$BITRATE"' \
    "$out_opus"

  # WAV -> WAV16k (PCM16)
  ffmpeg -y -loglevel error \
    -i "$f" \
    -ac 1 -ar '"$SR"' \
    -c:a pcm_s16le \
    "$out_wav"
'

echo "zip"
(
  cd "$(dirname "$TMP_WAV")"
  zip -r -q "$DST/wav.zip" "$(basename "$TMP_WAV")"
)
(
  cd "$(dirname "$TMP_OPUS")"
  zip -r -q "$DST/opus.zip" "$(basename "$TMP_OPUS")"
)

echo "clean"
rm -rf "$TMP_DIR" "$TMP_OPUS" "$TMP_WAV"
echo "done"