/**
 * Rebuilds the "See the heart behind the care" gallery on every location page as
 * a clean main-image + thumbnail-row gallery (uniform image sizes, thumbnails
 * below the main image). Clicking a thumbnail swaps the main image
 * (see .thc-gallery handler in site-interactions.js). Replaces the broken Slick
 * asNavFor slider (whose track computed to 0px because images lazy-load late).
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

  const h2 = ((/<h2[^>]*class="ba-h2[^"]*"[^>]*>([\s\S]*?)<\/h2>/.exec(block) || [])[1] || 'See the heart behind the care we provide').trim();
  const para = ((/<p>([\s\S]*?)<\/p>/.exec(block) || [])[1] || '').trim();

  const imgs = [];
  const seen = new Set();
  for (const im of block.matchAll(/<img[^>]*src="([^"]+)"[^>]*>/g)) {
    const src = im[1];
    const alt = (/alt="([^"]*)"/.exec(im[0]) || [, ''])[1];
    if (!seen.has(src)) { seen.add(src); imgs.push({ src, alt: alt || 'True Homecare carer' }); }
  }
  if (!imgs.length) continue;

  const thumbs = imgs
    .map((i, idx) => `<button type="button" class="thc-thumb${idx === 0 ? ' is-active' : ''}" data-full="${i.src}" aria-label="Show image ${idx + 1}"><img src="${i.src}" alt="${i.alt}" class="lazyload" loading="lazy"></button>`)
    .join('\n');

  const rebuilt = `<section class="block-image-gallery ba-gap-lg block-image-gallery-slider-trf">
<div class="container">
<div class="ba-section-desc text-center">
<h2 class="ba-h2 text-center">${h2}</h2>
<p>${para}</p>
</div>
<div class="thc-gallery">
<div class="thc-gallery-main"><img src="${imgs[0].src}" alt="${imgs[0].alt}" class="thc-gallery-main-img"></div>
<div class="thc-gallery-thumbs">
${thumbs}
</div>
</div>
</div>
</section>`;

  html = html.replace(sectionRe, rebuilt);
  writeFileSync(p, html, 'utf8');
  changed++;
}
console.log(`Rebuilt gallery on ${changed}/${files.length} location pages.`);
