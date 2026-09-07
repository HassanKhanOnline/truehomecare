/**
 * Generates per-page JSON-LD structured data from the mirror content and writes
 * it to site/src/data/page-schema.json as { route: [ ...ld+json objects ] }.
 * The Astro templates emit these into each page's <head>.
 *
 *   - Service pages -> FAQPage (from the on-page FAQ accordion)
 *   - Blog posts    -> BlogPosting + Person author (real date + author from markup)
 *
 * Site-wide Organization/LocalBusiness/WebSite schema lives in
 * src/components/SiteSchema.astro (static, real NAP data), not here.
 *
 * Run after content changes:  node scripts/generate-schema.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const ORIGIN = 'https://www.truehomecare.co.uk';
const pagesDir = join(root, 'site/src/mirror/pages');

const manifest = JSON.parse(
  readFileSync(join(root, 'site/src/data/mirror-manifest.json'), 'utf8')
);

const decode = (s = '') =>
  s
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#0?39;/g, "'")
    .replace(/&rsquo;/g, '’')
    .replace(/&lsquo;/g, '‘')
    .replace(/&rdquo;/g, '”')
    .replace(/&ldquo;/g, '“')
    .replace(/&quot;/g, '"')
    .replace(/&mdash;/g, '—')
    .replace(/&ndash;/g, '–')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim();

const MONTHS = {
  january: '01', february: '02', march: '03', april: '04', may: '05', june: '06',
  july: '07', august: '08', september: '09', october: '10', november: '11', december: '12',
};

// "15 June, 2024" | "27 December, 2024" -> "2024-06-15"
const isoDate = (text) => {
  const m = /(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})/.exec(text || '');
  if (!m) return null;
  const mm = MONTHS[m[2].toLowerCase()];
  if (!mm) return null;
  return `${m[3]}-${mm}-${String(m[1]).padStart(2, '0')}`;
};

// Extract FAQ Q&A pairs from a service page's dedicated FAQ accordion.
function extractFaq(html) {
  const questions = [
    ...html.matchAll(/class="faq-question"[^>]*>\s*<span>([\s\S]*?)<\/span>/g),
  ].map((m) => decode(m[1]));
  const answers = [
    ...html.matchAll(/class="faq-answer">([\s\S]*?)<\/div>/g),
  ].map((m) => decode(m[1]));
  const pairs = [];
  const n = Math.min(questions.length, answers.length);
  for (let i = 0; i < n; i++) {
    if (questions[i] && answers[i]) {
      pairs.push({
        '@type': 'Question',
        name: questions[i],
        acceptedAnswer: { '@type': 'Answer', text: answers[i] },
      });
    }
  }
  return pairs;
}

const schema = {};
let faqCount = 0;
let postCount = 0;

for (const p of manifest) {
  const html = readFileSync(join(pagesDir, p.file), 'utf8');
  const nodes = [];

  // Service pages -> FAQPage
  if (p.route.startsWith('/services/') && p.route !== '/services/') {
    const faqs = extractFaq(html);
    if (faqs.length) {
      nodes.push({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        '@id': `${ORIGIN}${p.route}#faq`,
        mainEntity: faqs,
      });
      faqCount++;
    }
  }

  // Blog posts -> BlogPosting + Person
  if (p.route.startsWith('/blog/') && p.route !== '/blog/') {
    const h1 = /<h1[^>]*>([\s\S]*?)<\/h1>/.exec(html);
    const authorBlock = /author-right-text"[^>]*>([\s\S]{0,200}?)<p class="date"/.exec(html);
    const dateText = /<p class="date">([^<]+)<\/p>/.exec(html);
    const headline = h1 ? decode(h1[1]) : decode(p.title);
    const author = authorBlock ? decode(authorBlock[1]) : '';
    const published = dateText ? isoDate(dateText[1]) : null;
    const img = /<img[^>]+src="(\/images\/[^"]+)"/.exec(
      html.slice(html.indexOf('single-post-content') > 0 ? html.indexOf('single-post-content') : 0)
    );

    const post = {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      '@id': `${ORIGIN}${p.route}#article`,
      mainEntityOfPage: `${ORIGIN}${p.route}`,
      headline,
      description: decode(p.description),
      author: {
        '@type': 'Person',
        name: author || 'Saima Adil Zafar',
        url: `${ORIGIN}/about-us-true-homecare/`,
      },
      publisher: { '@id': `${ORIGIN}/#organization` },
    };
    if (published) {
      post.datePublished = published;
      post.dateModified = published;
    }
    if (img) post.image = ORIGIN + img[1];
    nodes.push(post);
    postCount++;
  }

  if (nodes.length) schema[p.route] = nodes;
}

writeFileSync(
  join(root, 'site/src/data/page-schema.json'),
  JSON.stringify(schema, null, 2) + '\n',
  'utf8'
);

console.log(`Wrote page-schema.json: ${faqCount} FAQPage, ${postCount} BlogPosting (${Object.keys(schema).length} routes)`);
