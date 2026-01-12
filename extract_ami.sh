mkdir -p AMI

for f in *.tar.gz; do
  echo "Extracting $f ..."
  tar -xzf "$f" -C AMI
done
