import rss from '@astrojs/rss';
import { articles, articleUrl, SITE } from '../lib/site.js';

export function GET(context) {
  return rss({
    title: `${SITE.name} — Classements TOP 5`,
    description: SITE.description,
    site: context.site,
    items: articles.slice(0, 40).map((a) => ({
      title: a.title,
      description: a.content?.meta_description || a.excerpt,
      link: articleUrl(a.slug),
      pubDate: new Date(a.date),
      categories: [a.univers],
    })),
    customData: `<language>fr-FR</language>`,
  });
}
