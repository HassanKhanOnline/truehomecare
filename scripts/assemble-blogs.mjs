/**
 * Assembles the 3 new blog posts from shared chrome + per-post hero/sidebar +
 * the article bodies produced in scripts/blog-partials/. Writes the mirror
 * pages and prints the manifest entries to add.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const P = (p) => join(root, p);
const manifest = JSON.parse(readFileSync(P('site/src/data/mirror-manifest.json'), 'utf8'));
const routes = Object.fromEntries(manifest.map((m) => [m.route, m]));
const short = (t) => (t || '').replace(/&amp;/g, '&').replace(/\s*[|\-–].*True Homecare.*$/i, '').replace(/\s*-\s*True Homecare\s*$/i, '').trim();

const header = readFileSync(P('scripts/blog-partials/header.html'), 'utf8');
const footer = readFileSync(P('scripts/blog-partials/footer.html'), 'utf8');

const DATE = '2 September, 2026';
const recent = [
  '/blog/healthy-blood-pressure-by-age-uk/',
  '/blog/fall-prevention-elderly-home-care-support/',
  '/blog/uti-symptoms-elderly-people/',
  '/blog/loss-of-appetite-in-elderly-reasons/',
];

const posts = [
  {
    file: 'loneliness-in-older-people.html', route: '/loneliness-in-older-people/', body: 'body-loneliness.html',
    metaTitle: 'Loneliness in Older People: Companionship Support',
    metaDesc: 'Learn how companionship can support loneliness in older people through social connection, emotional support and meaningful activities at home.',
    h1: 'Loneliness in Older People: How Companionship Improves Wellbeing',
    hero: '/images/2025-06-truehomecare-companionship-at-home-e1750159124947.png',
    related: ['/blog/how-to-find-caregiver-for-elderly-parents/', '/blog/care-for-elderly-in-home/'],
  },
  {
    file: 'malnutrition-in-adults.html', route: '/malnutrition-in-adults/', body: 'body-malnutrition.html',
    metaTitle: 'Malnutrition for Elderly: Signs to Watch',
    metaDesc: 'Learn signs of malnutrition for elderly people, what to look for at home, and when eating difficulties may need support.',
    h1: 'Malnutrition for Elderly People: 10 Signs Your Loved One May Need Support With Eating',
    hero: '/images/2024-12-Meal-Preparation-Tips.jpg',
    related: ['/blog/loss-of-appetite-in-elderly-reasons/', '/blog/meal-plan-type-2-diabetes/'],
  },
  {
    file: 'female-bone-density-chart-by-age.html', route: '/female-bone-density-chart-by-age/', body: 'body-bone-density.html',
    metaTitle: 'Female Bone Density Chart by Age: A Guide',
    metaDesc: 'Explore a female bone density chart by age, understand bone changes, osteoporosis risk, and practical ways to support healthy ageing.',
    h1: 'Female Bone Density Chart by Age: Understanding Bone Changes, Osteoporosis Risk, and Healthy Ageing',
    hero: '/images/2025-06-Best-Chair-Exercises-for-Seniors-Boost-Strength-and-Flexibility-1.jpg',
    related: ['/blog/fall-prevention-elderly-home-care-support/', '/blog/posture-exercises-for-seniors/'],
  },
];

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const linkList = (slugs) =>
  slugs.map((r) => `<li><a href="${r}">${esc(short(routes[r] ? routes[r].title : r))}</a></li>`).join('\n');

const hero = (p) => `<section class="hero-location blog-hero hero-block hero-trf">
<div class="container">
<div class="row">
<div class="col-12 col-lg-4">
<div class="hero-location__information">
<div class="breadcrumbs-row">
<div class="breadcrumbs">
<span>
<span><a href="/">Home</a></span> &gt;
<span><a href="/blog">Blog</a></span> &gt;
<span class="breadcrumb_last" aria-current="page">${esc(p.h1)}</span>
</span>
</div>
</div>
<h1>${esc(p.h1)}</h1>
<div class="author-reviews-preview reviews-preview">
<img class="author-reviews-img lazyload" src="/images/2025-12-Saima.jpg" alt="Saima Adil Zafar">
<div class="author-right-text">
<p><a href="/about-us-true-homecare/">Saima Adil Zafar</a></p>
<p class="date">${DATE}</p>
</div>
</div>
</div>
</div>
<div class="col-12 col-lg-8">
<div class="hero-location__information max-w">
<img src="${p.hero}" alt="${esc(p.h1)}" class="lazyload">
</div>
</div>
</div>
</div>
</section>`;

const sidebar = (p) => `<div class="col-md-3">
<div class="related-post-wrapper">
<h2 class="title">Related Posts</h2>
<ul>
${linkList(p.related)}
</ul>
</div>
<div class="recent-post-wrapper">
<h2>Recent Posts</h2>
<ul>
${linkList(recent)}
</ul>
</div>
</div>`;

const newEntries = [];
for (const p of posts) {
  let body = readFileSync(P('scripts/blog-partials/' + p.body), 'utf8').trim();
  body = body.replace(/clients\.A companion/g, 'clients. A companion'); // fix export typo
  const content = `${hero(p)}
<section class="ba-gap-lg single-post-content-wrapper">
<div class="container">
<div class="row">
<div class="col-md-9 thc-article">
${body}
</div>
${sidebar(p)}
</div>
</div>
</section>
`;
  const full = header + content + footer;
  writeFileSync(P('site/src/mirror/pages/' + p.file), full, 'utf8');
  newEntries.push({ route: p.route, title: p.metaTitle, description: p.metaDesc, file: p.file, type: 'blog' });
  console.log(`wrote ${p.file} (${full.length} bytes)`);
}

console.log('\n=== manifest entries to add ===');
console.log(JSON.stringify(newEntries, null, 2));
