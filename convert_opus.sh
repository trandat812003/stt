SRC_DIR=/media/trandat/Data/phoaudiobook/audio
DST_DIR=/media/trandat/Data/phoaudiobook/opus
BITRATE=32k
SR=16000
JOBS=8

find "$SRC_DIR" -type f -name "*.wav" -print0 | \
xargs -0 -n 1 -P "$JOBS" bash -c '
  f="$0"

  out="'$DST_DIR'/${f#'$SRC_DIR'/}"
  out="${out%.wav}.opus"

  mkdir -p "$(dirname "$out")"

  ffmpeg -y -loglevel error \
    -i "$f" \
    -ac 1 \
    -ar '"$SR"' \
    -c:a libopus \
    -b:a '"$BITRATE"' \
    "$out"
'
