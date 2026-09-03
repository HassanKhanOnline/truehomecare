/**
 * Generates a Yoast-style, segmented XML sitemap set from the page manifest:
 *
 *   /sitemap_index.xml     - index referencing every segment below
 *   /page-sitemap.xml      - homepage + standalone pages (about, contact, blog index, ...)
 *   /service-sitemap.xml   - /services/*  (hub + individual services)
 *   /location-sitemap.xml  - /locations/* (hub + individual areas)
 *   /post-sitemap.xml      - individual /blog/<slug>/ articles
 *
 * <lastmod> per URL comes from the mtime of the page's mirror HTML file, so it
 * reflects when that page's content actually changed. Run after adding or
 * renaming pages:  node scripts/generate-sitemaps.mjs
 *
 * NB: there are no category/tag/author pages on this site, so no
 * category-sitemap.xml is produced (an empty sitemap would be flagged by GSC).
 */

import { readFileSync, writeFileSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const ORIGIN = 'https://www.truehomecare.co.uk';
const pagesDir = join(root, 'site/src/mirror/pages');

const manifest = JSON.parse(
  readFileSync(join(root, 'site/src/data/mirror-manifest.json'), 'utf8')
);

// W3C date (YYYY-MM-DD) from a file's mtime; falls back to today if missing.
const lastmodOf = (absFile) => {
  try {
    return statSync(absFile).mtime.toISOString().slice(0, 10);
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
};

// Build {loc, lastmod} for a manifest entry.
const entryUrl = (p) => ({
  loc: ORIGIN + p.route,
  lastmod: lastmodOf(join(pagesDir, p.file)),
});

// The homepage is not in the manifest; its content is home-body.html.
const home = {
  loc: ORIGIN + '/',
  lastmod: lastmodOf(join(root, 'site/src/mirror/home-body.html')),
};

// Partition every route into exactly one segment.
const segments = { page: [home], service: [], location: [], post: [] };
for (const p of manifest) {
  const r = p.route;
  if (r.startsWith('/services/')) segments.service.push(entryUrl(p));
  else if (r.startsWith('/locations/')) segments.location.push(entryUrl(p));
  else if (r.startsWith('/blog/') && r !== '/blog/') segments.post.push(entryUrl(p));
  else segments.page.push(entryUrl(p)); // standalone pages + /blog/ index
}

const bySlug = { page: 'page', service: 'service', location: 'location', post: 'post' };
const sort = (a, b) => a.loc.localeCompare(b.loc);

const xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>';

const urlset = (urls) =>
  `${xmlHeader}
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .sort(sort)
  .map((u) => `  <url>\n    <loc>${u.loc}</loc>\n    <lastmod>${u.lastmod}</lastmod>\n  </url>`)
  .join('\n')}
</urlset>
`;

// Write each non-empty segment; collect index rows with the segment's newest lastmod.
const indexRows = [];
for (const [key, urls] of Object.entries(segments)) {
  if (!urls.length) continue;
  const name = `${bySlug[key]}-sitemap.xml`;
  writeFileSync(join(root, 'site/public', name), urlset(urls), 'utf8');
  const newest = urls.map((u) => u.lastmod).sort().at(-1);
  indexRows.push({ loc: `${ORIGIN}/${name}`, lastmod: newest, count: urls.length });
}

const sitemapIndex = `${xmlHeader}
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${indexRows
  .map((s) => `  <sitemap>\n    <loc>${s.loc}</loc>\n    <lastmod>${s.lastmod}</lastmod>\n  </sitemap>`)
  .join('\n')}
</sitemapindex>
`;

writeFileSync(join(root, 'site/public/sitemap_index.xml'), sitemapIndex, 'utf8');

console.log('Wrote sitemap_index.xml + segments:');
indexRows.forEach((s) => console.log(`  ${String(s.count).padStart(3)} urls  ${s.loc}`));
