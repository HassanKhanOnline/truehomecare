/**
 * Generates per-page JSON-LD structured data from the mirror content and writes
 * it to site/src/data/page-schema.json as { route: [ ...ld+json objects ] }.
 * The Astro template (src/pages/[...slug].astro) emits these into each page's
 * <head>, in addition to the site-wide Organization/LocalBusiness/WebSite graph
 * from src/components/SiteSchema.astro.
 *
 *   - Location pages -> LocalBusiness (area-specific) + FAQPage (accordion FAQ)
 *   - Service pages  -> Service + FAQPage (classic or accordion FAQ)
 *   - Blog posts     -> BlogPosting (an Article subtype) + FAQPage (details FAQ)
 *   - FAQs page       -> FAQPage
 *
 * All contact data is the real UK NAP. Phone: +44 161 428 1989.
 *
 * Run after content changes:  node scripts/generate-schema.mjs
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const ORIGIN = 'https://www.truehomecare.co.uk';
const PHONE = '+44 161 428 1989';
const LOGO = `${ORIGIN}/images/2025-08-truehomecare-logo-1.png`;
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

const uniqQuestions = (pairs) => {
  const seen = new Set();
  const out = [];
  for (const p of pairs) {
    const key = p.name.toLowerCase();
    if (p.name && p.acceptedAnswer.text && !seen.has(key)) {
      seen.add(key);
      out.push(p);
    }
  }
  return out;
};

const mkQA = (q, a) => ({
  '@type': 'Question',
  name: q,
  acceptedAnswer: { '@type': 'Answer', text: a },
});

// 1) Classic service FAQ: .faq-question <span>…</span> + .faq-answer
function faqClassic(html) {
  const questions = [
    ...html.matchAll(/class="faq-question"[^>]*>\s*<span>([\s\S]*?)<\/span>/g),
  ].map((m) => decode(m[1]));
  const answers = [
    ...html.matchAll(/class="faq-answer">([\s\S]*?)<\/div>/g),
  ].map((m) => decode(m[1]));
  const pairs = [];
  const n = Math.min(questions.length, answers.length);
  for (let i = 0; i < n; i++) pairs.push(mkQA(questions[i], answers[i]));
  return uniqQuestions(pairs);
}

// 2) Bootstrap accordion FAQ (location pages + some service pages):
//    <button class="accordion-button …>Q</button> … <div class="accordion-body">A</div>
function faqAccordion(html) {
  const questions = [
    ...html.matchAll(/<button class="accordion-button[^>]*>([\s\S]*?)<\/button>/g),
  ].map((m) => decode(m[1]));
  const answers = [
    ...html.matchAll(/<div class="accordion-body">([\s\S]*?)<\/div>/g),
  ].map((m) => decode(m[1]));
  const pairs = [];
  const n = Math.min(questions.length, answers.length);
  for (let i = 0; i < n; i++) pairs.push(mkQA(questions[i], answers[i]));
  return uniqQuestions(pairs);
}

// 3) Blog <details> FAQ: .thc-faq-item > <summary>Q</summary> + .thc-faq-answer A
function faqDetails(html) {
  const items = [
    ...html.matchAll(/<details[^>]*class="[^"]*thc-faq-item[^"]*"[^>]*>([\s\S]*?)<\/details>/g),
  ];
  const pairs = [];
  for (const it of items) {
    const block = it[1];
    const q = /<summary[^>]*>([\s\S]*?)<\/summary>/.exec(block);
    const a = /class="thc-faq-answer"[^>]*>([\s\S]*?)<\/div>/.exec(block);
    if (q && a) pairs.push(mkQA(decode(q[1]), decode(a[1])));
  }
  return uniqQuestions(pairs);
}

const faqPageNode = (route, pairs) => ({
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  '@id': `${ORIGIN}${route}#faq`,
  mainEntity: pairs,
});

const BASE_ADDRESS = {
  '@type': 'PostalAddress',
  addressLocality: 'Stockport',
  addressRegion: 'Greater Manchester',
  addressCountry: 'GB',
};
const SERVICE_AREAS = ['Stockport', 'Wilmslow', 'Cheshire East', 'Greater Manchester'];

const schema = {};
let localCount = 0, serviceCount = 0, faqCount = 0, postCount = 0;

for (const p of manifest) {
  const html = readFileSync(join(pagesDir, p.file), 'utf8');
  const nodes = [];

  const isLocation = p.route.startsWith('/locations/') && p.route !== '/locations/';
  const isService = p.route.startsWith('/services/') && p.route !== '/services/';
  const isBlog = (p.route.startsWith('/blog/') && p.route !== '/blog/') || p.type === 'blog';
  const h1m = /<h1[^>]*>([\s\S]*?)<\/h1>/.exec(html);
  const h1 = h1m ? decode(h1m[1]) : decode(p.title);

  // -------- Location pages -> area-specific LocalBusiness --------
  if (isLocation) {
    const areaM = /data-location_name="([^"]+)"/.exec(html);
    const area = areaM ? areaM[1].trim() : h1.replace(/^Home Care in\s*/i, '');
    nodes.push({
      '@context': 'https://schema.org',
      '@type': 'LocalBusiness',
      '@id': `${ORIGIN}${p.route}#localbusiness`,
      name: `True Homecare — ${area}`,
      url: `${ORIGIN}${p.route}`,
      telephone: PHONE,
      image: LOGO,
      logo: LOGO,
      priceRange: '££',
      description: decode(p.description),
      address: BASE_ADDRESS,
      areaServed: { '@type': 'Place', name: area },
      parentOrganization: { '@id': `${ORIGIN}/#organization` },
    });
    localCount++;

    const faqs = faqAccordion(html);
    if (faqs.length) { nodes.push(faqPageNode(p.route, faqs)); faqCount++; }
  }

  // -------- Service pages -> Service (+ FAQPage) --------
  if (isService) {
    nodes.push({
      '@context': 'https://schema.org',
      '@type': 'Service',
      '@id': `${ORIGIN}${p.route}#service`,
      name: h1,
      serviceType: h1,
      description: decode(p.description),
      url: `${ORIGIN}${p.route}`,
      provider: { '@id': `${ORIGIN}/#organization` },
      areaServed: SERVICE_AREAS.map((a) => ({ '@type': 'Place', name: a })),
    });
    serviceCount++;

    let faqs = faqClassic(html);
    if (!faqs.length) faqs = faqAccordion(html);
    if (faqs.length) { nodes.push(faqPageNode(p.route, faqs)); faqCount++; }
  }

  // -------- Blog posts -> BlogPosting (Article subtype) (+ FAQPage) --------
  if (isBlog) {
    const authorBlock = /author-right-text"[^>]*>([\s\S]{0,200}?)<p class="date"/.exec(html);
    const dateText = /<p class="date">([^<]+)<\/p>/.exec(html);
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
      headline: h1,
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

    const faqs = faqDetails(html);
    if (faqs.length) { nodes.push(faqPageNode(p.route, faqs)); faqCount++; }
  }

  // -------- Dedicated FAQs page -> FAQPage --------
  if (!isLocation && !isService && !isBlog && /faqs?/i.test(p.route)) {
    let faqs = faqClassic(html);
    if (!faqs.length) faqs = faqAccordion(html);
    if (faqs.length) { nodes.push(faqPageNode(p.route, faqs)); faqCount++; }
  }

  if (nodes.length) schema[p.route] = nodes;
}

writeFileSync(
  join(root, 'site/src/data/page-schema.json'),
  JSON.stringify(schema, null, 2) + '\n',
  'utf8'
);

console.log(
  `Wrote page-schema.json: ${localCount} LocalBusiness, ${serviceCount} Service, ` +
  `${postCount} BlogPosting, ${faqCount} FAQPage (${Object.keys(schema).length} routes)`
);
