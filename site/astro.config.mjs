// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://www.truehomecare.co.uk',
  integrations: [sitemap()],
  prefetch: {
    prefetchAll: true,
  },
  server: {
    // Use the port assigned by the preview harness, fall back to 4325.
    port: Number(process.env.PORT) || 4325,
  },
});
