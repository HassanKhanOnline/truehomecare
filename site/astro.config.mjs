// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
// Sitemaps are generated as a Yoast-style segmented set (sitemap_index.xml +
// per-type segment files) by scripts/generate-sitemaps.mjs, so the built-in
// @astrojs/sitemap chunked generator is intentionally not used.
export default defineConfig({
  site: 'https://www.truehomecare.co.uk',
  integrations: [],
  prefetch: {
    prefetchAll: true,
  },
  server: {
    // Use the port assigned by the preview harness, fall back to 4325.
    port: Number(process.env.PORT) || 4325,
  },
});
