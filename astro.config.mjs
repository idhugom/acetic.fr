// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Site canonique (domaine final). Les slugs sont préservés à l'identique
// pour ne pas casser le référencement existant.
export default defineConfig({
  site: 'https://acetic.fr',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
    inlineStylesheets: 'auto',
  },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
    }),
  ],
  image: {
    // Optimisation build-time (webp/avif responsive) via Sharp.
    responsiveStyles: true,
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  },
  vite: {
    build: {
      assetsInlineLimit: 0,
    },
  },
});
