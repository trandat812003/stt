#!/usr/bin/env bash
# set -e

P=gigaspeech

SRC_DIR=/media/trandat/DataVoice/${P}/

# TMP_DIR=/tmp/${P}_extract
TMP_OPUS=/tmp/${P}/opus/
TMP_WAV=/tmp/${P}/wav/

DST=/media/trandat/DataVoice/opus/

BITRATE=32k
SR=16000
JOBS=8

mkdir -p "$TMP_OPUS" "$DST" 


find "$SRC_DIR" -type f \( \
  -name "*.zip" -o \
  -name "*.tar" -o \
  -name "*.tar.gz" -o \
  -name "*.tgz" -o \
  -name "*.rar" \
\) -print0 | while IFS= read -r -d '' f; do
archive_name="$(basename "$f")"
  archive_stem="${archive_name%%.*}"
  echo $archive_stem

    TMP_DIR=/tmp/${archive_stem}

    mkdir -p "$TMP_DIR"
  
  echo "Extracting: $f"

  case "$f" in
    *.zip)
      unzip -oq "$f" -d "$TMP_DIR"
      ;;
    *.tar)
      tar -xf "$f" -C "$TMP_DIR"
      ;;
    *.tar.gz|*.tgz)
      tar -xzf "$f" -C "$TMP_DIR"
      ;;
    *.rar)
      unrar x -o+ "$f" "$TMP_DIR" >/dev/null
      ;;
  esac

  
  parent_name="$(basename "$(dirname "$f")")"
  echo "$parent_name"

  echo "convert."
  find "$TMP_DIR" -type f -name "*.wav" -print0 | \
  xargs -0 -n 1 -P "$JOBS" bash -c '
  f="$0"

  # path tương đối trong /tmp
  rel="${f#"'$TMP_DIR'/"}"
#   rel="${rel#audio/}"

  out_opus="'$TMP_OPUS'/${rel%.wav}.opus"

  mkdir -p "$(dirname "$out_opus")" "$(dirname "$out_wav")"

  # WAV -> OPUS
  ffmpeg -y -loglevel error \
    -i "$f" \
    -ac 1 -ar '"$SR"' \
    -c:a libopus -b:a '"$BITRATE"' \
    "$out_opus"
  '
echo "$(realpath -m "${TMP_OPUS}/${archive_stem}")"
(
  cd "$TMP_OPUS" || exit 1
  mkdir -p "$DST/$parent_name/"
  zip -r -q "$DST/$parent_name/${archive_stem}.zip" "$archive_stem"
) && rm -f "$f" && rm -rf "$TMP_DIR" "$(realpath -m "${TMP_OPUS}/${archive_stem}")"
done

echo "done"
