import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const P = (f) => join(root, 'site/src/mirror/pages/', f);

const data = {
  'how-to-find-caregiver-for-elderly-parents': { img: '/images/2025-10-How-to-Find-a-Caregiver-for-Elderly-Parents-What-You-Need-to-Know-1.jpg', title: 'How to Find a Caregiver for Elderly Parents: What You Need to Know', date: '8 October, 2025' },
  'care-for-elderly-in-home': { img: '/images/2024-04-Care-for-Elderly-in-Home-10-Signs-Your-Elderly-Parent-Needs-Help-1.jpg', title: 'Care for Elderly in Home: 10 Signs Your Elderly Parent Needs Help', date: '15 April, 2024' },
  'loss-of-appetite-in-elderly-reasons': { img: '/images/2026-03-8-Reasons-for-Loss-of-Appetite-in-Elderly.jpg', title: '8 Reasons for Loss of Appetite in Elderly', date: '25 March, 2026' },
  'meal-plan-type-2-diabetes': { img: '/images/2024-12-7-Day-Meal-Plan-for-Type-2-Diabetes-An-Ultimate-Guide.jpg', title: '7-Day Meal Plan for Type 2 Diabetes: An Ultimate Guide', date: '27 December, 2024' },
  'fall-prevention-elderly-home-care-support': { img: '/images/2026-07-Can-Home-Care-Reduce-the-Risk-of-Falls-in-Older-Adults.jpg', title: 'Can Home Care Reduce the Risk of Falls in Older Adults?', date: '15 June, 2026' },
  'posture-exercises-for-seniors': { img: '/images/2025-10-Top-5-simple-Posture-Exercises-for-Seniors-to-Do-at-Home.jpg', title: 'Top 5 simple Posture Exercises for Seniors to Do at Home', date: '30 October, 2025' },
};

const posts = {
  'blog__loneliness-in-older-people.html': ['how-to-find-caregiver-for-elderly-parents', 'care-for-elderly-in-home'],
  'blog__malnutrition-in-adults.html': ['loss-of-appetite-in-elderly-reasons', 'meal-plan-type-2-diabetes'],
  'blog__female-bone-density-chart-by-age.html': ['fall-prevention-elderly-home-care-support', 'posture-exercises-for-seniors'],
};

const escAttr = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
const escHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const item = (slug) => {
  const d = data[slug];
  const url = '/blog/' + slug + '/';
  return `<li>
<a href="${url}"><img src="${d.img}" alt="${escAttr(d.title)}" class="lazyload"></a>
<p class="excerpt"><a href="${url}">${escHtml(d.title)}</a></p>
<p class="date">${d.date}</p>
</li>`;
};

for (const [file, related] of Object.entries(posts)) {
  let h = readFileSync(P(file), 'utf8');
  const ul = `<ul>\n${related.map(item).join('\n')}\n</ul>`;
  const re = /(<div class="related-post-wrapper">\s*<h2 class="title">Related Posts<\/h2>\s*)<ul>[\s\S]*?<\/ul>/;
  if (!re.test(h)) { console.log(`${file}: related-post-wrapper NOT matched`); continue; }
  h = h.replace(re, `$1${ul}`);
  writeFileSync(P(file), h, 'utf8');
  console.log(`${file}: Related Posts updated (${related.length} cards)`);
}
