import data from '../data/articles.json';

export const SITE = {
  name: 'Acetic',
  domain: 'https://www.acetic.fr',
  tagline: 'Le média des classements TOP 5',
  description:
    "Acetic.fr décrypte et classe le meilleur de chaque univers en TOP 5 : tech, argent, bien-être, maison, food, voyage… Des palmarès clairs, comparés et argumentés pour décider vite et bien.",
  twitter: '@acetic_fr',
};

export const articles = data.articles;
export const universList = data.univers;
export const generatedRatio = data.generated_ratio;

export function slugifyUnivers(name) {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/&/g, 'et')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function universWithSlug() {
  return universList.map((u) => ({ ...u, slug: slugifyUnivers(u.name) }));
}

export function articlesByUnivers(name) {
  return articles.filter((a) => a.univers === name);
}

export function findUniversBySlug(slug) {
  const u = universList.find((u) => slugifyUnivers(u.name) === slug);
  return u ? u.name : null;
}

export function getArticle(slug) {
  return articles.find((a) => a.slug === slug);
}

/** URL d'un article — structure IDENTIQUE au WordPress d'origine (/top5/{slug}.htm)
 *  pour préserver 100% du référencement et des backlinks existants. */
export function articleUrl(slug) {
  return `/top5/${slug}.htm`;
}

/** URL d'un univers (pages en répertoire -> slash final pour éviter toute redirection). */
export function universUrl(slug) {
  return `/univers/${slug}/`;
}

export function related(article, n = 3) {
  const same = articles.filter((a) => a.univers === article.univers && a.slug !== article.slug);
  const others = articles.filter((a) => a.univers !== article.univers && a.slug !== article.slug);
  return [...same, ...others].slice(0, n);
}

export function readingTime(article) {
  if (article.content?.reading_time_min) return article.content.reading_time_min;
  const words = (article.old_html || '').split(/\s+/).length;
  return Math.max(3, Math.round(words / 200));
}

/** Univers -> couleur/emoji d'accent pour la variété visuelle */
export const UNIVERS_META = {
  'Tech & Numérique': { accent: 'var(--cyan)', emoji: '⚡' },
  'Argent & Finance': { accent: 'var(--lime)', emoji: '📈' },
  'Bien-être & Santé': { accent: 'var(--good)', emoji: '🌿' },
  'Maison & Déco': { accent: 'var(--gold)', emoji: '🏠' },
  'Food & Cuisine': { accent: 'var(--pink)', emoji: '🍽️' },
  'Voyage & Loisirs': { accent: 'var(--violet)', emoji: '✈️' },
  'Mode & Style': { accent: 'var(--pink)', emoji: '✦' },
  'Auto & Mobilité': { accent: 'var(--cyan)', emoji: '🏁' },
  'Animaux': { accent: 'var(--gold)', emoji: '🐾' },
  'Éducation & Carrière': { accent: 'var(--violet)', emoji: '🎓' },
  'Culture & Divertissement': { accent: 'var(--pink)', emoji: '🎬' },
  'Famille & Enfants': { accent: 'var(--good)', emoji: '👨‍👩‍👧' },
};

export function universMeta(name) {
  return UNIVERS_META[name] || { accent: 'var(--lime)', emoji: '★' };
}
