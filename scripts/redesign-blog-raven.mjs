/**
 * Rebuilds /blog/ index into a Raven-style layout:
 *   featured hero (image left, text right) + category filter bar (counts + sort)
 *   + single-column list cards (thumbnail left, content right).
 * Keeps the existing header/hero chrome and the newsletter/footer tail.
 * Filter/sort behaviour lives in site-interactions.js.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const P = (p) => join(root, p);
const BLOG = P('site/src/mirror/pages/blog.html');
const posts = JSON.parse(readFileSync(join(process.env.TMP, 'blog-posts-full.json'), 'utf8'));

const MONTHS = { january:0,february:1,march:2,april:3,may:4,june:5,july:6,august:7,september:8,october:9,november:10,december:11 };
const parseDate = (s) => {
  const m = /(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})/.exec(s || '');
  return m ? new Date(+m[3], MONTHS[m[2].toLowerCase()] ?? 0, +m[1]) : new Date(0);
};

// Balanced topic buckets by title keyword (priority order).
const CATS = [
  { id: 'dementia', label: "Dementia & Alzheimer's", re: /dementia|alzheimer|cognitive|frontotemporal/i },
  { id: 'nutrition', label: 'Nutrition & Diet', re: /meal|diet|nutrition|appetite|malnutrition|diabet|weight|dehydrat|hydration|eating|food/i },
  { id: 'mobility', label: 'Mobility & Safety', re: /fall|posture|exercise|mobility|gadget|chair|safety|balance/i },
  { id: 'conditions', label: 'Health Conditions', re: /stroke|parkinson|blood pressure|bone|osteo|vision|\buti\b|disease|symptom|arthritis|incontinence|pressure/i },
  { id: 'homecare', label: 'Home Care & Support', re: /.*/ },
];
const catOf = (title) => CATS.find((c) => c.re.test(title)) || CATS[CATS.length - 1];

for (const p of posts) { p._d = parseDate(p.date); const c = catOf(p.title); p.catId = c.id; p.catLabel = c.label; }
posts.sort((a, b) => b._d - a._d); // latest first

const counts = {};
for (const p of posts) counts[p.catId] = (counts[p.catId] || 0) + 1;

const esc = (s) => (s || '').replace(/&amp;/g, '&').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const escT = (s) => (s || '').replace(/&#0?39;/g, '’').replace(/&#8217;/g, '’').replace(/&amp;/g, '&').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const iso = (d) => d.toISOString().slice(0, 10);

const featured = posts[0];
const rest = posts.slice(1);

const featuredHtml = `<section class="thc-blog-featured">
<div class="container">
<a class="thc-feat-card" href="${featured.url}">
<div class="thc-feat-img"><img src="${featured.img}" alt="${esc(featured.title)}" class="lazyload"></div>
<div class="thc-feat-body">
<div class="thc-feat-meta"><span class="thc-badge">Featured</span><span class="thc-cat thc-cat--${featured.catId}">${escT(featured.catLabel)}</span><span class="thc-date">${featured.date}</span></div>
<h2>${escT(featured.title)}</h2>
<p>${escT(featured.excerpt)}</p>
<span class="thc-readlink">Read the Article &rarr;</span>
</div>
</a>
</div>
</section>`;

const pill = (id, label, n, active) =>
  `<button class="thc-fpill${active ? ' is-active' : ''}" data-cat="${id}">${escT(label)} <span>${n}</span></button>`;
const filterHtml = `<section class="thc-blog-filter">
<div class="container">
<div class="thc-filter-row">
<div class="thc-filter-cats">
${pill('all', 'All', posts.length, true)}
${CATS.filter((c) => counts[c.id]).map((c) => pill(c.id, c.label, counts[c.id], false)).join('\n')}
</div>
<div class="thc-blog-search">
<input type="search" id="thc-blog-search" class="thc-blog-search-input" placeholder="Search articles…" aria-label="Search the blog" autocomplete="off">
</div>
<div class="thc-filter-sort">
<label for="thc-sort">Sort</label>
<select id="thc-sort" class="thc-sort"><option value="latest">Latest</option><option value="oldest">Oldest</option><option value="az">Title A–Z</option></select>
</div>
</div>
</div>
</section>`;

const card = (p) => `<a class="thc-post" href="${p.url}" data-cat="${p.catId}" data-date="${iso(p._d)}" data-title="${esc(p.title)}">
<div class="thc-post-img"><img src="${p.img}" alt="${esc(p.title)}" class="lazyload"></div>
<div class="thc-post-body">
<div class="thc-post-meta"><span class="thc-cat thc-cat--${p.catId}">${escT(p.catLabel)}</span><span class="thc-date">${p.date}</span></div>
<h3>${escT(p.title)}</h3>
<p>${escT(p.excerpt)}</p>
<span class="thc-author">Saima Adil Zafar</span>
</div>
</a>`;

const listHtml = `<section class="thc-blog-list">
<div class="container">
<div class="thc-list" id="thc-blog-list">
${rest.map(card).join('\n')}
</div>
<p class="thc-noresults" hidden>No articles in this category yet.</p>
</div>
</section>`;

const middle = `\n${featuredHtml}\n${filterHtml}\n${listHtml}\n`;

// Splice into the existing page: keep head (through hero close) + tail (newsletter onward).
let html = readFileSync(BLOG, 'utf8');
const headEnd = html.indexOf('<section class="ba-features quality-block');
const tailStart = html.indexOf('<section class="thc-blog-newsletter">');
if (headEnd < 0 || tailStart < 0) throw new Error('markers not found (head:' + headEnd + ' tail:' + tailStart + ')');
const head = html.slice(0, headEnd);
const tail = html.slice(tailStart);
writeFileSync(BLOG, head + middle + tail, 'utf8');

console.log('Rebuilt blog.html');
console.log('featured:', featured.title.slice(0, 50));
console.log('category counts:', JSON.stringify(counts));
console.log('list cards:', rest.length);
