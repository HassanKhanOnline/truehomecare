#!/usr/bin/env python3
"""Crawl all live True Homecare pages and mirror them into the Astro build."""
import urllib.request, re, os, json

BASE='https://www.truehomecare.co.uk'
SITE='/Users/hassankhan/Documents/truehomecare/site'
MIRDIR=SITE+'/src/mirror/pages'
os.makedirs(MIRDIR, exist_ok=True)
hdr={'User-Agent':'Mozilla/5.0'}
MENU=open(SITE+'/src/mirror/menu.html').read()

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=hdr),timeout=45).read().decode('utf-8','replace')

def balanced_replace(html, start_pat, tag, new):
    m=re.search(start_pat, html)
    if not m: return html
    i=m.start(); depth=0; j=len(html)
    for t in re.finditer(r'<(%s)\b|</(%s)>'%(tag,tag), html, re.I):
        if t.start()<i: continue
        if t.group(1): depth+=1
        else:
            depth-=1
            if depth==0: j=t.end(); break
    return html[:i]+new+html[j:]

def localize(inner):
    inner=re.sub(r'<script[^>]*>.*?</script>','',inner,flags=re.S)
    inner=re.sub(r'<noscript[^>]*>.*?</noscript>','',inner,flags=re.S)
    # trustindex divs -> script (handle before generic lazyload)
    inner=re.sub(r'<div([^>]*?)\sdata-src=["\'](?:https?:)?//cdn\.trustindex\.io/loader\.js\?([a-z0-9]+)["\']([^>]*)>\s*</div>',
                 r"<script defer async src='https://cdn.trustindex.io/loader.js?\2'></script>", inner)
    # remove mobile duplicate trustindex wrappers
    inner=re.sub(r'<div class="[^"]*-mobile[^"]*">\s*<script[^>]*cdn\.trustindex\.io[^>]*>\s*</script>\s*</div>','',inner,flags=re.S)
    # lazyload images
    inner=re.sub(r'src=["\']data:image[^"\']*["\']','',inner)
    inner=re.sub(r'\sdata-sizes=["\'][^"\']*["\']','',inner)
    inner=re.sub(r'\sstyle=["\']--smush[^"\']*["\']','',inner)
    inner=re.sub(r'data-src=(["\'][^"\']+["\'])', r'src=\1', inner)
    inner=re.sub(r'data-srcset=(["\'][^"\']+["\'])', r'srcset=\1', inner)
    # bg-image (fix &#039; entity)
    inner=re.sub(r'data-bg-image=["\']url\((?:&#039;|\'|")?([^"\')]+?)(?:&#039;|\'|")?\)["\']',
                 lambda m: f'style="background-image:url(\'{m.group(1)}\')"', inner)
    inner=re.sub(r'style=["\']background-image:inherit;?["\']','',inner)
    # localize domain
    for d in ('https://www.truehomecare.co.uk','http://www.truehomecare.co.uk','//www.truehomecare.co.uk'):
        inner=inner.replace(d,'')
    # swap menu
    inner=balanced_replace(inner, r'<ul id="main-menu"', 'ul', MENU)
    return inner

def slug_to_route(url):
    p=url.replace(BASE,'').strip('/')
    return '/'+p+'/' if p else '/'

def slug_to_file(url):
    p=url.replace(BASE,'').strip('/')
    return (p if p else 'index').replace('/','__')+'.html'

urls=[u for u in open('/private/tmp/claude-501/-Users-hassankhan/39a34293-635b-4bb2-a94d-0d56458279c2/scratchpad/all_urls.txt').read().split('\n') if u.strip()]
manifest=[]
assets=set()
css_all=set()
fail=[]
for n,url in enumerate(urls,1):
    try:
        h=get(url)
    except Exception as e:
        fail.append((url,str(e)[:40])); continue
    # title + desc
    tm=re.search(r'<title>(.*?)</title>', h, re.S); title=re.sub(r'\s+',' ',tm.group(1)).strip() if tm else ''
    dm=re.search(r'<meta name="description" content="([^"]*)"', h); desc=dm.group(1) if dm else ''
    cm=re.search(r'<link rel="canonical" href="([^"]*)"', h); canon=cm.group(1) if cm else url
    # css links
    for c in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', h):
        mm=re.search(r'href=["\']([^"\']+)', c)
        if not mm: continue
        u=mm.group(1)
        if u.startswith('//'): u='https:'+u
        if 'truehomecare.co.uk' in u: css_all.add(re.sub(r'https?://www\.truehomecare\.co\.uk','',u).split('?')[0])
    # body
    bm=re.search(r'<body[^>]*>(.*)</body>', h, re.S)
    if not bm: fail.append((url,'no body')); continue
    inner=localize(bm.group(1))
    # collect assets from localized inner
    for m in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', inner):
        if m.startswith('/wp-') and re.search(r'\.(jpg|jpeg|png|webp|svg|gif|ico)$', m.split('?')[0], re.I):
            assets.add(m.split('?')[0])
    for m in re.findall(r"url\('([^']+)'\)", inner):
        if m.startswith('/wp-'): assets.add(m.split('?')[0])
    for ss in re.findall(r'srcset=["\']([^"\']+)["\']', inner):
        for part in ss.split(','):
            u=part.strip().split(' ')[0]
            if u.startswith('/wp-') and re.search(r'\.(jpg|jpeg|png|webp|svg|gif)$',u,re.I): assets.add(u.split('?')[0])
    fn=slug_to_file(url)
    open(MIRDIR+'/'+fn,'w').write(inner)
    manifest.append({'route':slug_to_route(url),'title':title,'description':desc,'file':fn})
    if n%20==0: print(f"  ...{n}/{len(urls)}")

json.dump(manifest, open(SITE+'/src/data/mirror-manifest.json','w'), indent=1, ensure_ascii=False)
json.dump(sorted(css_all), open(SITE+'/src/data/mirror-css.json','w'), indent=1)
open('/private/tmp/claude-501/-Users-hassankhan/39a34293-635b-4bb2-a94d-0d56458279c2/scratchpad/mirror_assets.txt','w').write('\n'.join(sorted(assets)))
print(f"\nMIRRORED {len(manifest)} pages | CSS variants {len(css_all)} | assets {len(assets)} | failed {len(fail)}")
for f in fail: print("  FAIL",f)
