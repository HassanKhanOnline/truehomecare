/**
 * Generates the AI-facing discovery files from the page manifest:
 *
 *   site/public/llms.txt        - llms.txt convention (markdown index for LLMs)
 *   site/public/entitymap.json  - EntityMap v1.0 (entitymap.org)
 *   site/public/entitymap.html  - human/crawler-readable view of the same data
 *
 * Run after adding or renaming pages:  node scripts/generate-ai-files.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const ORIGIN = 'https://www.truehomecare.co.uk';
const PHONE = '0161 428 1989';

const manifest = JSON.parse(
  readFileSync(join(root, 'site/src/data/mirror-manifest.json'), 'utf8')
);

// The manifest stores titles/descriptions as raw HTML; decode for plain-text output.
const decode = (s = '') =>
  s
    .replace(/&amp;/g, '&')
    .replace(/&#0?39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .trim();

// Strip the trailing brand suffix so link labels read cleanly in a list.
const shortTitle = (t) =>
  decode(t)
    .replace(/\s*[|\-–]\s*True Homecare\s*$/i, '')
    .replace(/\s*-\s*True Homecare\s*$/i, '')
    .trim();

const esc = (s = '') =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const byRoute = Object.fromEntries(manifest.map((p) => [p.route, p]));
const group = (pred) => manifest.filter((p) => pred(p.route));

const services = group((r) => r.startsWith('/services/') && r !== '/services/');
const locations = group((r) => r.startsWith('/locations/') && r !== '/locations/');
const blog = group((r) => r.startsWith('/blog/'));
const core = group(
  (r) => !r.startsWith('/services/') && !r.startsWith('/locations/') && !r.startsWith('/blog/')
);

const generated = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');

/* ------------------------------------------------------------------ *
 * llms.txt
 * ------------------------------------------------------------------ */

const summary =
  'CQC-registered home care provider delivering personalised care in clients’ own homes ' +
  'across Stockport, Wilmslow, Cheshire East and Greater Manchester.';

const linkLine = (p) => {
  const d = decode(p.description);
  return `- [${shortTitle(p.title)}](${ORIGIN}${p.route})${d ? `: ${d}` : ''}`;
};

const llms = `# True Homecare

> ${summary}

True Homecare is a family-run domiciliary care company based in Stockport, England. Care is
delivered in the client's own home rather than a residential setting, and ranges from short
visiting calls through to 24-hour live-in support. The service holds a 'Good' rating from the
Care Quality Commission (CQC), the independent regulator of health and social care in England.

Enquiries: ${PHONE} · ${ORIGIN}/contact-us/

## Services

${services.map(linkLine).join('\n')}

## Locations served

${locations.map(linkLine).join('\n')}

## About and policies

${core.map(linkLine).join('\n')}

## Guides and articles

${blog.map(linkLine).join('\n')}

## Notes

- All care is regulated by the Care Quality Commission (CQC).
- Coverage is limited to Stockport, Cheshire East and surrounding parts of Greater Manchester.
- Content describes services offered by True Homecare and is not a substitute for medical advice.
`;

writeFileSync(join(root, 'site/public/llms.txt'), llms, 'utf8');

/* ------------------------------------------------------------------ *
 * entitymap.json  (spec: https://entitymap.org/spec/v1.0)
 * ------------------------------------------------------------------ */

// Authoritative references, used only where the mapping is unambiguous.
const SAME_AS = {
  'personal-care': 'https://en.wikipedia.org/wiki/Personal_care',
  'live-in-care': 'https://en.wikipedia.org/wiki/Live-in_caregiver',
  'domiciliary-care': 'https://en.wikipedia.org/wiki/Home_care',
  'palliative-care': 'https://en.wikipedia.org/wiki/Palliative_care',
  'end-of-life-care': 'https://en.wikipedia.org/wiki/End-of-life_care',
  'respite-care': 'https://en.wikipedia.org/wiki/Respite_care',
  'dementia-and-alzheimer-care': 'https://en.wikipedia.org/wiki/Dementia',
  'parkinsons-care': "https://en.wikipedia.org/wiki/Parkinson's_disease",
  'stroke-care': 'https://en.wikipedia.org/wiki/Stroke',
};

const PLACES = [
  ['Stockport', 'https://en.wikipedia.org/wiki/Stockport', '/locations/stockport/',
    'Metropolitan borough in Greater Manchester, England, and the base of operations for True Homecare.'],
  ['Wilmslow', 'https://en.wikipedia.org/wiki/Wilmslow', '/locations/cheshire/wilmslow/',
    'Town in Cheshire East, England, within True Homecare’s service area.'],
  ['Cheshire', 'https://en.wikipedia.org/wiki/Cheshire', '/locations/cheshire/',
    'Ceremonial county in North West England; True Homecare serves the Cheshire East area.'],
  ['Greater Manchester', 'https://en.wikipedia.org/wiki/Greater_Manchester', '/locations/greater-manchester/',
    'Metropolitan county in North West England covering Stockport and surrounding towns.'],
  ['Cheadle', 'https://en.wikipedia.org/wiki/Cheadle,_Greater_Manchester', '/locations/cheadle/',
    'Town in the Metropolitan Borough of Stockport served by True Homecare.'],
];

const slugOf = (route) => route.replace(/^\/services\//, '').replace(/\/$/, '');
const pad = (n) => String(n).padStart(3, '0');

const entities = [];

// The publisher itself.
entities.push({
  entityId: 'e_001',
  '@type': 'Organization',
  name: 'True Homecare',
  description:
    'Family-run, CQC-registered domiciliary care provider delivering personalised care in ' +
    "clients' own homes across Stockport, Wilmslow, Cheshire East and Greater Manchester. " +
    "Holds a 'Good' rating from the Care Quality Commission.",
  sameAs: ORIGIN,
  relations: [],
  hasChunks: [
    {
      chunkId: 'c_001',
      text: summary,
      sourceUrl: `${ORIGIN}/about-us-true-homecare/`,
      pageTitle: 'About True Homecare',
      publisher: 'True Homecare',
      retrieved: generated,
      contentType: 'evidence',
    },
  ],
});

let n = 1;
const orgRelations = entities[0].relations;

// One entity per service page.
for (const p of services) {
  n += 1;
  const id = `e_${pad(n)}`;
  const slug = slugOf(p.route);
  const name = shortTitle(p.title);
  const entity = {
    entityId: id,
    '@type': 'Service',
    name,
    description: decode(p.description),
    relations: [
      { predicate: 'PROVIDED_BY', targetId: 'e_001', targetName: 'True Homecare', confidence: 'declared' },
    ],
    hasChunks: [
      {
        chunkId: `c_${pad(n)}`,
        text: decode(p.description),
        sourceUrl: `${ORIGIN}${p.route}`,
        pageTitle: name,
        publisher: 'True Homecare',
        retrieved: generated,
        relevanceScore: 0.95,
        contentType: 'evidence',
      },
    ],
  };
  if (SAME_AS[slug]) entity.sameAs = SAME_AS[slug];
  entities.push(entity);
  orgRelations.push({ predicate: 'PROVIDES', targetId: id, targetName: name, confidence: 'declared' });
}

// Related-service links that are true of this provider.
const link = (fromName, toName, predicate) => {
  const a = entities.find((e) => e.name === fromName);
  const b = entities.find((e) => e.name === toName);
  if (a && b) a.relations.push({ predicate, targetId: b.entityId, targetName: b.name, confidence: 'declared' });
};
link('End of Life Care Services at Home', 'Palliative Care at Home', 'RELATED_TO');
link('Post-Operative Care at Home', 'After-Hospital Care at Home in Stockport', 'RELATED_TO');
link('Short Break Care Services in Stockport', 'Respite Care at Home in Stockport & Wilmslow', 'RELATED_TO');

// Place entities.
for (const [name, sameAs, route, description] of PLACES) {
  n += 1;
  const id = `e_${pad(n)}`;
  entities.push({
    entityId: id,
    '@type': 'Place',
    name,
    description,
    sameAs,
    relations: [
      { predicate: 'SERVED_BY', targetId: 'e_001', targetName: 'True Homecare', confidence: 'declared' },
    ],
    hasChunks: byRoute[route]
      ? [
          {
            chunkId: `c_${pad(n)}`,
            text: decode(byRoute[route].description),
            sourceUrl: `${ORIGIN}${route}`,
            pageTitle: shortTitle(byRoute[route].title),
            publisher: 'True Homecare',
            retrieved: generated,
            relevanceScore: 0.9,
            contentType: 'evidence',
          },
        ]
      : [],
  });
  orgRelations.push({ predicate: 'OPERATES_IN', targetId: id, targetName: name, confidence: 'declared' });
}

const entitymap = {
  version: '1.0',
  schema: 'https://entitymap.org/spec/v1.0',
  publisher: { name: 'True Homecare', url: ORIGIN },
  generated,
  entities,
};

writeFileSync(join(root, 'site/public/entitymap.json'), JSON.stringify(entitymap, null, 2) + '\n', 'utf8');

/* ------------------------------------------------------------------ *
 * entitymap.html  (human + crawler readable view of the same data)
 * ------------------------------------------------------------------ */

const entityCard = (e) => `
      <article class="entity" id="${esc(e.entityId)}">
        <header>
          <h3>${esc(e.name)}</h3>
          <p class="ids">
            <span class="tag">${esc(e['@type'])}</span>
            <code>${esc(e.entityId)}</code>
            ${e.sameAs ? `<a href="${esc(e.sameAs)}" rel="noopener">sameAs</a>` : ''}
          </p>
        </header>
        <p class="desc">${esc(e.description)}</p>
        ${
          e.relations.length
            ? `<ul class="rel">${e.relations
                .map(
                  (r) =>
                    `<li><span class="pred">${esc(r.predicate)}</span> <a href="#${esc(
                      r.targetId
                    )}">${esc(r.targetName)}</a></li>`
                )
                .join('')}</ul>`
            : ''
        }
        ${
          e.hasChunks.length
            ? `<div class="ev">${e.hasChunks
                .map(
                  (c) =>
                    `<blockquote>${esc(c.text)}<cite><a href="${esc(c.sourceUrl)}">${esc(
                      c.pageTitle
                    )}</a></cite></blockquote>`
                )
                .join('')}</div>`
            : ''
        }
      </article>`;

const byType = (t) => entities.filter((e) => e['@type'] === t);

const html = `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EntityMap | True Homecare</title>
<meta name="description" content="Human-readable view of True Homecare's EntityMap: the entities this site covers, how they relate, and the pages that evidence them.">
<link rel="alternate" type="application/json" href="/entitymap.json">
<style>
  :root{--ink:#14201c;--soft:#47554f;--mute:#6c7a74;--line:#dae2de;--bg:#f6f8f7;--card:#fff;--green:#266751;--orange:#c4501f}
  @media (prefers-color-scheme:dark){:root{--ink:#eaf1ee;--soft:#b4c2bc;--mute:#8b9b94;--line:#2c3b36;--bg:#101613;--card:#182220;--green:#6fbf9c;--orange:#e8834f}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
  .wrap{max-width:900px;margin:0 auto;padding:48px 20px 80px}
  h1{font-size:32px;line-height:1.15;margin:0 0 10px;letter-spacing:-.01em}
  .lede{color:var(--soft);max-width:62ch;margin:0 0 8px}
  .meta{font:13px/1.7 ui-monospace,Menlo,monospace;color:var(--mute);border-top:1px solid var(--line);padding-top:16px;margin-top:24px}
  .meta a{color:var(--green)}
  h2{font-size:20px;margin:44px 0 4px;letter-spacing:-.01em}
  .count{color:var(--mute);font:12px/1 ui-monospace,Menlo,monospace;margin:0 0 16px}
  .entity{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:18px 20px;margin-bottom:12px}
  .entity h3{margin:0 0 6px;font-size:17px}
  .ids{margin:0 0 10px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font:12px/1 ui-monospace,Menlo,monospace}
  .tag{background:var(--green);color:var(--bg);padding:3px 7px;border-radius:2px;letter-spacing:.04em}
  .ids code{color:var(--mute)}
  .ids a{color:var(--orange)}
  .desc{margin:0 0 12px;color:var(--soft)}
  ul.rel{list-style:none;margin:0 0 12px;padding:0;display:flex;flex-wrap:wrap;gap:6px}
  ul.rel li{font:12px/1 ui-monospace,Menlo,monospace;border:1px solid var(--line);border-radius:2px;padding:5px 8px}
  .pred{color:var(--orange)}
  ul.rel a{color:var(--ink);text-decoration:none}
  ul.rel a:hover{text-decoration:underline}
  blockquote{margin:0;padding:12px 14px;border-left:2px solid var(--green);background:var(--bg);color:var(--soft);font-size:14px;border-radius:0 2px 2px 0}
  cite{display:block;margin-top:8px;font-style:normal;font-size:12px}
  cite a{color:var(--green)}
  footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);color:var(--mute);font-size:13px}
  footer a{color:var(--green)}
</style>
</head>
<body>
<div class="wrap">
  <h1>EntityMap</h1>
  <p class="lede">A structured, entity-first index of what this site knows &mdash; the entities True Homecare
  covers, how they relate to one another, and the pages that evidence each one.</p>
  <p class="lede">This is the human-readable view. The machine-readable source is
  <a href="/entitymap.json">/entitymap.json</a>, following the
  <a href="https://entitymap.org/spec/v1.0" rel="noopener">EntityMap v1.0</a> specification.</p>
  <p class="meta">
    Publisher: <a href="${ORIGIN}">True Homecare</a><br>
    Entities: ${entities.length} &middot; Generated: ${generated}<br>
    See also: <a href="/llms.txt">/llms.txt</a> &middot; <a href="/sitemap-index.xml">/sitemap-index.xml</a>
  </p>

  <h2>Organisation</h2>
  <p class="count">${byType('Organization').length} entity</p>
  ${byType('Organization').map(entityCard).join('')}

  <h2>Services</h2>
  <p class="count">${byType('Service').length} entities</p>
  ${byType('Service').map(entityCard).join('')}

  <h2>Places</h2>
  <p class="count">${byType('Place').length} entities</p>
  ${byType('Place').map(entityCard).join('')}

  <footer>
    Generated from the site page manifest. Regenerate with
    <code>node scripts/generate-ai-files.mjs</code>.
  </footer>
</div>
</body>
</html>
`;

writeFileSync(join(root, 'site/public/entitymap.html'), html, 'utf8');

console.log(
  `Wrote llms.txt (${services.length} services, ${locations.length} locations, ${blog.length} articles), ` +
    `entitymap.json (${entities.length} entities), entitymap.html`
);
