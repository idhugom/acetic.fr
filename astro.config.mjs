// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Site canonique (domaine final). Les slugs sont préservés à l'identique
// pour ne pas casser le référencement existant.
export default defineConfig({
  site: 'https://www.acetic.fr',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
    inlineStylesheets: 'auto',
  },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      // Les pages d'articles sont post-traitées en /top5/{slug}.htm : on réécrit
      // les URLs du sitemap en conséquence.
      serialize(item) {
        item.url = item.url.replace(/\/top5\/([^/]+)\/?$/, '/top5/$1.htm');
        return item;
      },
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
