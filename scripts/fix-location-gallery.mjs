/**
 * Replaces the broken "See the heart behind the care" Slick gallery on every
 * location page with a clean static gallery (heading + intro + one responsive
 * row of carer photos), removing the conflicting two-row slider markup.
 */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dir = join(root, 'site/src/mirror/pages');
const files = readdirSync(dir).filter((f) => f.startsWith('locations__') && f.endsWith('.html'));

const sectionRe = /<section class="[^"]*block-image-gallery-slider-trf[^"]*">[\s\S]*?<\/section>/;

let changed = 0;
for (const file of files) {
  const p = join(dir, file);
  let html = readFileSync(p, 'utf8');
  const m = sectionRe.exec(html);
  if (!m) continue;
  const block = m[0];

  const h2 = (/<h2[^>]*>([\s\S]*?)<\/h2>/.exec(block) || [])[1] || 'See the heart behind the care we provide';
  const para = (/<p>([\s\S]*?)<\/p>/.exec(block) || [])[1] || '';

  // Collect image srcs (dedupe; the thumb + content rows repeat the same images).
  const imgs = [];
  const seen = new Set();
  for (const im of block.matchAll(/<img[^>]*src="([^"]+)"[^>]*>/g)) {
    const src = im[1];
    const alt = (/alt="([^"]*)"/.exec(im[0]) || [, ''])[1];
    if (!seen.has(src)) { seen.add(src); imgs.push({ src, alt }); }
  }

  const gallery = imgs
    .map((i) => `<figure class="thc-carer-img"><img src="${i.src}" alt="${i.alt || 'True Homecare carer'}" class="lazyload" loading="lazy"></figure>`)
    .join('\n');

  const rebuilt = `<section class="block-image-gallery ba-gap-lg block-image-gallery-slider-trf">
<div class="container">
<div class="ba-section-desc text-center">
<h2 class="ba-h2 text-center">${h2.trim()}</h2>
<p>${para.trim()}</p>
</div>
<div class="thc-carer-gallery">
${gallery}
</div>
</div>
</section>`;

  html = html.replace(sectionRe, rebuilt);
  writeFileSync(p, html, 'utf8');
  changed++;
}

console.log(`Rebuilt gallery on ${changed}/${files.length} location pages.`);
