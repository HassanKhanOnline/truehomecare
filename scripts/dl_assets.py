#!/usr/bin/env python3
import urllib.request, os
DEST='/Users/hassankhan/Documents/truehomecare/site/public'
hdr={'User-Agent':'Mozilla/5.0'}
assets=[a for a in open('/private/tmp/claude-501/-Users-hassankhan/39a34293-635b-4bb2-a94d-0d56458279c2/scratchpad/mirror_assets.txt').read().split('\n') if a.strip()]
ok=have=fail=0
for a in assets:
    out=DEST+a
    if os.path.exists(out): have+=1; continue
    os.makedirs(os.path.dirname(out),exist_ok=True)
    try:
        d=urllib.request.urlopen(urllib.request.Request('https://www.truehomecare.co.uk'+a,headers=hdr),timeout=25).read()
        open(out,'wb').write(d); ok+=1
    except Exception as e: fail+=1; print("FAIL",a,str(e)[:30])
print(f"DONE downloaded={ok} already={have} fail={fail} total={len(assets)}")
