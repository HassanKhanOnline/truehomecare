#!/bin/bash
# Download used images from live site into public/, preserving wp-content/uploads path.
LIST="/private/tmp/claude-501/-Users-hassankhan/39a34293-635b-4bb2-a94d-0d56458279c2/scratchpad/used_images.txt"
DEST="/Users/hassankhan/Documents/truehomecare/site/public"
ok=0; fail=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  path="${url#https://www.truehomecare.co.uk/}"
  out="$DEST/$path"
  mkdir -p "$(dirname "$out")"
  if [ -f "$out" ]; then ok=$((ok+1)); continue; fi
  if curl -fsSL --max-time 40 "$url" -o "$out"; then ok=$((ok+1)); else fail=$((fail+1)); rm -f "$out"; echo "FAIL: $url"; fi
done < "$LIST"
echo "DONE. ok=$ok fail=$fail"
