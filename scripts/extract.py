#!/usr/bin/env python3
"""Extract True Homecare WordPress WXR export into clean JSON data files for the Astro build."""
import re, json, os, html

XML = '/Users/hassankhan/Downloads/truehomecare.WordPress.2026-07-07.xml'
OUT = '/Users/hassankhan/Documents/truehomecare/site/src/data'
os.makedirs(OUT, exist_ok=True)

xml = open(XML, 'r', encoding='utf-8', errors='replace').read()
items = re.findall(r'<item>(.*?)</item>', xml, re.S)

def field(block, tag):
    m = re.search(r'<%s>(?:<!\[CDATA\[(.*?)\]\]>)?(.*?)</%s>' % (re.escape(tag), re.escape(tag)), block, re.S)
    if not m: return ''
    return (m.group(1) if m.group(1) is not None else m.group(2) or '').strip()

def metas(block):
    """Return dict of meta_key -> meta_value (last wins for repeaters we handle separately)."""
    out = {}
    for m in re.finditer(
        r'<wp:postmeta>\s*<wp:meta_key>(?:<!\[CDATA\[(.*?)\]\]>)?\s*</wp:meta_key>\s*'
        r'<wp:meta_value>(?:<!\[CDATA\[(.*?)\]\]>)?\s*</wp:meta_value>\s*</wp:postmeta>',
        block, re.S):
        k = (m.group(1) or '').strip()
        v = (m.group(2) or '')
        out[k] = v
    return out

def yoast(mv):
    return {
        'title': mv.get('_yoast_wpseo_title', ''),
        'description': mv.get('_yoast_wpseo_metadesc', ''),
        'canonical': mv.get('_yoast_wpseo_canonical', ''),
        'focus_kw': mv.get('_yoast_wpseo_focuskw', ''),
    }

def build_id_maps():
    """Map attachment ID -> URL for resolving ACF image fields."""
    att = {}
    for it in items:
        if field(it, 'wp:post_type') == 'attachment':
            pid = field(it, 'wp:post_id')
            url = field(it, 'wp:attachment_url')
            att[pid] = url
    return att

ATT = build_id_maps()
def img(v):
    v = (v or '').strip()
    if v.isdigit():
        return ATT.get(v, '')
    return v

def repeater(mv, prefix, subfields):
    """Collect ACF repeater rows: prefix_<i>_<sub> -> list of dicts."""
    rows = {}
    for k, v in mv.items():
        m = re.match(r'^%s_(\d+)_(.+)$' % re.escape(prefix), k)
        if m:
            i = int(m.group(1)); sub = m.group(2)
            rows.setdefault(i, {})[sub] = v
    return [rows[i] for i in sorted(rows) if not (len(subfields)==1 and not rows[i].get(subfields[0]))]

# ---------- LOCATIONS ----------
locations = []
for it in items:
    if field(it, 'wp:post_type') != 'location': continue
    if field(it, 'wp:status') != 'publish': continue
    mv = metas(it)
    slug = field(it, 'wp:post_name')
    areas = [r.get('area_served','') for r in repeater(mv, 'areas_served', ['area_served'])]
    areas = [a for a in areas if a]
    # "Why families trust" value cards use suffixed keys _icon_title_1.._3
    P = 'localize_product_differences_section_localize_differences_icons_localize_differences_'
    cards = []
    for i in (1, 2, 3):
        t = mv.get(f'{P}icon_title_{i}', '').strip()
        d = mv.get(f'{P}icon_description_{i}', '').strip()
        ic = img(mv.get(f'{P}icons_{i}', ''))
        if t or d:
            cards.append({'title': t, 'description': d, 'icon': ic})
    gallery = []
    for k in sorted(mv.keys()):
        m = re.match(r'location_list_gallery_gallery_images_(\d+)_image$', k)
        if m and mv[k]:
            gallery.append(img(mv[k]))
    locations.append({
        'slug': slug,
        'title': field(it, 'title'),
        'hero_heading': mv.get('location_main_heading', ''),
        'hero_subheading': mv.get('location_main_sub_heading', ''),
        'hero_description': mv.get('location_main_heading_description', ''),
        'locality': mv.get('address_locality', ''),
        'region': mv.get('address_region', ''),
        'phone': mv.get('phone', ''),
        'email': mv.get('email', ''),
        'areas_served': areas,
        'value_cards': cards,
        'value_heading': mv.get('localize_product_differences_section_localize_differences_heading', ''),
        'value_description': mv.get('localize_product_differences_section_localize_differences_description', ''),
        'about': mv.get('about_us', ''),
        'about_image': img(mv.get('about_city_image','')),
        'gallery': gallery,
        'google_reviews_url': mv.get('location_what_our_customer_say_google_business_url', '') or mv.get('location_what_our_customer_say_google_business_profile_url',''),
        'seo': yoast(mv),
    })

# ---------- PAGES ----------
SERVICE_SLUGS = {'personal-care','domiciliary-care','dementia-and-alzheimer-care','companionship',
    'live-in-care','overnight-care','palliative-care','parkinsons-care','private-care','respite-care',
    'stroke-care','reablement-services','learning-disability-support','physical-disability-support',
    'long-term-condition-support','end-of-life-care'}
CMS_SLUGS = {'your-care-planning-process','understanding-the-role-of-homecare-professionals',
    'your-safety-and-wellbeing','support-for-those-who-support-others','being-there-for-you',
    'terms-and-conditions','privacy-policy'}

pages = []
for it in items:
    if field(it, 'wp:post_type') != 'page': continue
    if field(it, 'wp:status') != 'publish': continue
    mv = metas(it)
    slug = field(it, 'wp:post_name')
    pages.append({
        'slug': slug,
        'title': field(it, 'title'),
        'content': field(it, 'content:encoded'),
        'kind': 'service' if slug in SERVICE_SLUGS else ('cms' if slug in CMS_SLUGS else 'page'),
        'seo': yoast(mv),
    })

# ---------- POSTS (blog) ----------
posts = []
for it in items:
    if field(it, 'wp:post_type') != 'post': continue
    if field(it, 'wp:status') != 'publish': continue
    mv = metas(it)
    posts.append({
        'slug': field(it, 'wp:post_name'),
        'title': html.unescape(field(it, 'title')),
        'date': field(it, 'wp:post_date'),
        'content': field(it, 'content:encoded'),
        'excerpt': field(it, 'excerpt:encoded'),
        'seo': yoast(mv),
    })

# ---------- TESTIMONIALS ----------
tst = []
for it in items:
    if field(it, 'wp:post_type') != 'testimonials': continue
    tst.append({'title': field(it, 'title'), 'content': field(it, 'content:encoded')})

def dump(name, data):
    p = os.path.join(OUT, name)
    json.dump(data, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"  {name}: {len(data)} records")

print("Extracted:")
dump('locations.json', locations)
dump('pages.json', pages)
dump('blog-posts.json', posts)
dump('testimonials.json', tst)
print("\nService pages found:", sorted([p['slug'] for p in pages if p['kind']=='service']))
print("\nSample location (Cheshire) areas_served:", next((l['areas_served'] for l in locations if l['slug']=='cheshire'), None))
print("Sample location value_cards count:", next((len(l['value_cards']) for l in locations if l['slug']=='cheshire'), None))
