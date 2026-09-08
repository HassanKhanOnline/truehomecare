import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const P = (f) => join(root, 'site/src/mirror/pages/', f);

const posts = [
  {
    file: 'loneliness-in-older-people.html',
    heroOld: '/images/2025-06-truehomecare-companionship-at-home-e1750159124947.png',
    hero: '/images/blog-loneliness-0.jpg',
    secs: [
      ['What Causes Loneliness in Older People', '/images/blog-loneliness-1.jpg'],
      ['When Is Additional Home Care Needed', '/images/blog-loneliness-2.jpg'],
    ],
  },
  {
    file: 'malnutrition-in-adults.html',
    heroOld: '/images/2024-12-Meal-Preparation-Tips.jpg',
    hero: '/images/blog-malnutrition-0.jpg',
    secs: [
      ['Who Is Most at Risk of Malnutrition?', '/images/blog-malnutrition-1.jpg'],
      ['When Should You Seek Professional Advice?', '/images/blog-malnutrition-2.jpg'],
    ],
  },
  {
    file: 'female-bone-density-chart-by-age.html',
    heroOld: '/images/2025-06-Best-Chair-Exercises-for-Seniors-Boost-Strength-and-Flexibility-1.jpg',
    hero: '/images/blog-bone-density-0.jpg',
    secs: [
      ['What Does a Female Bone Density Chart by Age Show?', '/images/blog-bone-density-1.jpg'],
      ['How Does Menopause Affect Bone Density?', '/images/blog-bone-density-2.jpg'],
      ['Can Osteoporosis Affect Life Expectancy?', '/images/blog-bone-density-3.jpg'],
    ],
  },
];

const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const escAttr = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;');

for (const p of posts) {
  let h = readFileSync(P(p.file), 'utf8');
  if (!h.includes(p.hero)) h = h.replace(p.heroOld, p.hero);
  let inserted = 0;
  for (const [heading, img] of p.secs) {
    const re = new RegExp('(<h2 id="[^"]*">' + escRe(heading) + '</h2>)');
    const fig = '\n<figure class="thc-fig"><img src="' + img + '" alt="' + escAttr(heading) + '" class="lazyload" loading="lazy" /></figure>';
    if (re.test(h) && !h.includes('src="' + img + '"')) {
      h = h.replace(re, '$1' + fig);
      inserted++;
    }
  }
  writeFileSync(P(p.file), h, 'utf8');
  console.log(`${p.file}: hero=${h.includes(p.hero) ? 'set' : 'MISSING'}, section imgs inserted=${inserted}/${p.secs.length}`);
}
