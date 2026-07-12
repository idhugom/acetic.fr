# Acetic.fr — Le média des classements TOP 5

Refonte complète du site [acetic.fr](https://acetic.fr) : un média éditorial 100 % dédié aux
**classements TOP 5**, au design kinétique et premium. Site statique **Astro** (SSG),
déployé sur **Cloudflare Pages**.

- **Preprod :** https://acetic.pages.dev
- **Production (à venir) :** https://acetic.fr

## ✨ Ce qui a été fait

- **Design 100 % original** orienté « classement / podium / leaderboard » : typographie
  géante (Anton), numéros de rang or/argent/bronze, palette électrique (lime), fonds
  auroraux animés, grain.
- **Animations fluides** : smooth-scroll (Lenis), reveals au scroll + compteurs (GSAP),
  transitions de page (Astro View Transitions), boutons magnétiques, ticker, barre de
  progression de lecture, sommaire scrollspy.
- **85 articles migrés** depuis le WordPress d'origine : **slug et titre 100 % identiques**,
  **image à la une réutilisée** (optimisée en WebP responsive par Astro).
- **Contenu entièrement régénéré** par IA (`gpt-5.6-terra`, Responses API + Batch API),
  en sortie structurée : intro, TL;DR « featured snippet », critères de classement,
  **tableau comparatif**, 5 fiches notées avec **pros/cons en 2 colonnes**, **encarts**
  d'information, **FAQ**, verdict, méthodologie.
- **SEO** : slugs préservés, sitemap, RSS, robots, Open Graph, JSON-LD
  (Article + ItemList + FAQPage + BreadcrumbList).

## 🧱 Stack

| | |
|---|---|
| Framework | [Astro 5](https://astro.build) (SSG, sortie `dist/`) |
| Animations | GSAP (ScrollTrigger) · Lenis · Astro View Transitions |
| Images | `astro:assets` + Sharp (WebP/AVIF responsive au build) |
| Polices | Anton · Space Grotesk · Inter (variables, auto-hébergées) |
| Hébergement | Cloudflare Pages |

## 🚀 Développement

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # génère dist/
npm run preview  # prévisualise dist/
```

## 🔁 Pipeline de contenu (régénération)

Les scripts de génération vivent dans `scripts/` :

1. `fetch_posts.py` — récupère titres, slugs, images et ancien contenu via l'API REST WordPress.
2. `download_images.py` — télécharge les images à la une dans `src/assets/posts/`.
3. `build_batch.py` — construit le fichier de tâches et lance le **Batch API** OpenAI.
4. `build_articles.py` — fusionne WordPress + sortie IA + images → `src/data/articles.json`
   (consommé par le site). Repli automatique sur l'ancien contenu tant que l'IA n'a pas répondu.

Nécessite `OPENAI_API_KEY` dans l'environnement.

## ☁️ Déploiement Cloudflare Pages

### Déploiement automatique (GitHub → Pages)

Le workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) build et déploie
à chaque `push` sur `main` (et crée des **previews** sur les Pull Requests).

**Secrets GitHub requis** (Settings → Secrets and variables → Actions) :

| Secret | Valeur |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Token API Cloudflare (permission *Pages: Edit*) |
| `CLOUDFLARE_ACCOUNT_ID` | ID du compte Cloudflare |

> Tant que ces secrets ne sont pas renseignés, l'étape de déploiement est ignorée
> (le build continue de valider le site).

### Paramètres de build (si intégration Git native Cloudflare)

- **Branche de production :** `main`
- **Commande de build :** `npm run build`
- **Répertoire de sortie :** `dist`
- **Répertoire racine :** *(vide)*
- **Commentaires de build (previews) :** activés

### Domaine personnalisé & DNS — **configuré**

Réalisé automatiquement via l'API Cloudflare :

1. Domaines perso ajoutés au projet Pages : `www.acetic.fr` (**principal / canonique**) et `acetic.fr` (apex).
2. Enregistrements DNS créés : `CNAME www → acetic.pages.dev` et `CNAME acetic.fr → acetic.pages.dev` (proxifiés).

**Reste 1 étape manuelle** (le token API fourni n'a pas la permission « Redirect Rules ») —
**redirection apex → www** : Cloudflare → zone `acetic.fr` → **Rules → Redirect Rules → Create** :
- *Quand* `Hostname` **equals** `acetic.fr` → *Redirection statique/dynamique 301* vers
  `concat("https://www.acetic.fr", http.request.uri.path)`, **Preserve query string** activé.

Le site est configuré avec **`www.acetic.fr`** comme URL canonique, et les URLs d'articles
reproduisent **à l'identique** la structure d'origine `/top5/{slug}.htm` (aucune URL indexée cassée).
