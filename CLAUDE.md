# CLAUDE.md — Acetic.fr

Guide de travail pour Claude Code sur ce dépôt. À lire **au début de chaque session**.
Ce fichier ne modifie pas le site : c'est le mode d'emploi éditorial et technique qui vient
**compléter** l'existant.

---

## Règles d'intervention Claude (impératives)

### Règle n°1 — TOUJOURS travailler sur `main` (très important)

Toute session — développement, rédaction, amélioration, correction, etc. — se fait
**directement sur la branche `main`** du dépôt GitHub. Ne **JAMAIS** créer de branche ni
travailler sur une branche secondaire. On commit et on push sur `main`.

> Chaque push sur `main` déclenche le déploiement production (GitHub Actions →
> Cloudflare Pages). Vérifier le build en local (`npm run build`) **avant** de pousser.

### Règle n°2 — Toujours en qualité optimale

Se placer systématiquement dans le réglage **le plus performant / le plus « intelligent »**
du modèle pour chaque intervention (rédaction, code, analyse).
**Seule exception :** la génération de la photo OpenAI se fait en `quality: "medium"` (voir §6).

### Règle n°3 — Clés API / tokens (jamais en dur)

Les clés et tokens nécessaires sont fournis par **l'environnement cloud de Claude Code**
(variables d'environnement, `process.env` / `os.environ`). On les **récupère depuis
l'environnement** — on ne les redemande pas et on ne les écrit **jamais en dur** dans le
code, un fichier versionné ou un commit.

Variables attendues :

| Variable | Usage |
|---|---|
| `OPENAI_API_KEY` | Génération des **images** de couverture (OpenAI) |
| `OPENAI_IMAGE_MODEL` | Modèle image (défaut projet : `gpt-image-2`) |
| `OPENAI_TEXT_MODEL` | Modèle texte du **pipeline legacy** uniquement (voir §0) |
| `CLOUDFLARE_API_TOKEN` | Déploiement Cloudflare Pages |
| `CLOUDFLARE_ACCOUNT_ID` | Compte Cloudflare |

---

## Le projet en bref (repères techniques)

- **Site :** Acetic.fr — *le média des classements TOP 5*. Média éditorial français, design
  premium/kinétique (podium, leaderboard).
- **Stack :** Astro 5 (SSG, sortie `dist/`) · GSAP · Lenis · Astro View Transitions ·
  `astro:assets` + Sharp (WebP/AVIF responsive) · polices Anton / Space Grotesk / Inter.
- **Hébergement :** Cloudflare Pages. Déploiement auto à chaque `push` sur `main`
  (`.github/workflows/deploy.yml`), previews sur PR.
- **Domaine canonique :** `https://www.acetic.fr`.
- **URLs articles :** `/top5/{slug}.htm` (structure d'origine WordPress **préservée à
  l'identique** — ne jamais casser un slug existant). Pages d'univers : `/univers/{slug}/`.
- **Source de vérité du contenu :** **`src/data/articles.json`** (objet
  `{ generated_ratio, univers[], articles[] }`). C'est ce fichier que le site consomme.
- **Images :** `src/assets/posts/{fichier}` ; le champ `image` d'un article contient **juste
  le nom de fichier** (ex. `mon-slug.jpg`). Optimisation build-time automatique.

### Carte des fichiers utiles

| Chemin | Rôle |
|---|---|
| `src/data/articles.json` | **Les articles** (à éditer directement pour publier) |
| `src/pages/top5/[slug].astro` | Gabarit d'un article + JSON-LD (Article, ItemList, FAQPage, Breadcrumb) |
| `src/components/ArticleContent.astro` | Rendu du corps riche (schéma ci-dessous) |
| `src/lib/site.js` | Helpers : `articleUrl`, `related`, univers, `SITE` |
| `src/lib/images.js` | Résolution des images `src/assets/posts/*` |
| `scripts/gen_common.py`, `build_batch.py`, `fetch_*` | **Pipeline legacy** (migration WP) — voir §0 |

> ⚠️ **Ne pas relancer** `scripts/build_articles.py` pour publier : il reconstruit
> `articles.json` depuis les seules sources WordPress et **écraserait** les articles rédigés
> par Claude. Les nouveaux articles s'ajoutent **directement** dans `src/data/articles.json`.

---

## Règles de rédaction

### 0. Règles d'or (prioritaires)

- **Rédaction par Claude, pas par l'API.** Le contenu des articles est écrit par **toi,
  Claude** (réglage le plus intelligent), **directement en session**. Le pipeline OpenAI
  texte (`gpt-5.6-terra` via Batch/Responses API dans `scripts/`) est **legacy** : il a servi
  à régénérer les 85 articles migrés depuis WordPress. Pour tout **nouvel** article, c'est
  Claude qui rédige. **Seules les images** passent encore par OpenAI (§6).
- **Anti-cannibalisation.** Sujet libre ⇒ vérifier d'abord l'existant. Chaque nouvel article
  doit porter sur un sujet **distinct** de ceux déjà publiés (§3).
- **Qualité avant tout.** Chaque article doit être **la référence** sur son sujet : détails
  concrets en plus et, selon la pertinence, éléments riches (tableau, comparaison, astuces,
  FAQ, citation, chiffres…). Ce sont des exemples — pas besoin de tout mettre à chaque fois (§4).
- **Photo OpenAI obligatoire.** Jamais publier sans visuel. Toujours une **vraie photo à la
  une, ultra réaliste, générée par OpenAI** avant publication (§6).
- **Liens internes.** Ajouter **1 à 4 liens internes** par article vers d'autres pages du
  site (§5).

### 1. Le site — ligne éditoriale

Acetic.fr est **le média des classements TOP 5** : sur chaque sujet, un palmarès de
**exactement 5 éléments**, du meilleur (rang 1) au 5ᵉ, clair, comparé et argumenté, pour
**décider vite et bien**. Le lecteur type cherche à choisir (un produit, une méthode, une
destination, une appli…) et veut à la fois une réponse express (« l'essentiel ») et de quoi
tout comprendre.

Le contenu se répartit en **12 univers** (valeurs exactes du champ `univers`, ne pas en
inventer) :

`Tech & Numérique` · `Argent & Finance` · `Bien-être & Santé` · `Maison & Déco` ·
`Food & Cuisine` · `Voyage & Loisirs` · `Mode & Style` · `Auto & Mobilité` · `Animaux` ·
`Éducation & Carrière` · `Culture & Divertissement` · `Famille & Enfants`.

### 2. Identité & ton

- **Français impeccable**, expert mais **accessible**, vivant, direct. Zéro remplissage,
  zéro phrase « creuse » ni générique.
- **Utile et concret** : conseils actionnables, chiffres et ordres de grandeur crédibles,
  cas d'usage, pièges à éviter, critères de choix.
- **Honnête (E-E-A-T).** Ne pas inventer de fausses données trop précises (prix exacts,
  dates de sortie) : rester sur des **fourchettes / ordres de grandeur** en cas de doute.
  Assumer une méthodologie de classement transparente (`methodology_html`).
- **Actualité 2026.** Écrire au présent d'aujourd'hui.
- Style « classement / podium » : accroches punchy, verdict tranché, badges (« Meilleur
  choix », « Meilleur rapport qualité-prix », « Coup de cœur », « Petit budget »…).

### 3. Avant d'écrire — anti-cannibalisation

1. **Lire l'existant** : parcourir `title`/`slug`/`univers` de tous les articles dans
   `src/data/articles.json` (87 articles à ce jour).
2. **Choisir un angle réellement neuf.** Si un sujet proche existe, changer d'angle, de cible
   ou de sous-thème pour ne pas se cannibaliser en SEO. Deux articles ne doivent pas viser la
   même intention de recherche / le même mot-clé principal.
3. **Slug unique et stable.** Un slug ne se réutilise ni ne se modifie une fois publié
   (les URLs `/top5/{slug}.htm` sont indexées). Slug court, en minuscules, sans accent, mots
   séparés par des tirets.

### 4. Qualité rédactionnelle — schéma de contenu

Le corps d'article est un objet **`content`** (dans `articles.json`) rendu par
`ArticleContent.astro`. Structure attendue (respecter les bornes) :

| Champ | Contenu |
|---|---|
| `meta_title` | Titre SEO, **45–62 caractères**, contient le sujet |
| `meta_description` | **140–160 caractères**, engageante |
| `hook` | Sous-titre punchy en une phrase |
| `univers` | L'un des 12 univers (§1) |
| `reading_time_min` | Entier (minutes) |
| `keywords` | **5–8** mots-clés SEO |
| `intro_html` | Intro (2–3 `<p>`) qui pose l'intention de recherche |
| `quick_answer` | `{ summary_html` (TL;DR type *featured snippet*)`, winner, winner_reason }` |
| `criteria` | **3–5** critères `{ name, why }` (méthode de classement) |
| `items` | **EXACTEMENT 5** fiches, rang 1→5 (voir ci-dessous) |
| `comparison` | `{ title, columns` (1ʳᵉ = « Critère », puis 1 par item)`, rows[{cells}] }` |
| `callouts` | **2–4** encarts `{ type, title, html }`, `type` ∈ `astuce\|info\|attention\|eco\|budget` |
| `faq` | **4–6** `{ question, answer_html }` (vraies questions des lecteurs) |
| `verdict_html` | Conclusion qui aide à décider |
| `methodology_html` | Court paragraphe méthodo (transparence) |

Chaque **item** : `{ rank, name, tagline, badge, rating` (note /5, **une décimale**, ex.
`4.6`)`, price_hint` (fourchette ou `"—"`)`, best_for, body_html` (2–4 `<p>` riches et
concrets)`, pros` (**3–4**)`, cons` (**1–3**) `}`.

**HTML des champs `*_html` : uniquement** `<p>`, `<ul>`/`<li>`, `<strong>`, `<em>`, `<a>`.
Pas de `<h1>`–`<h6>`, pas de style inline, pas de script. (Sans objet `content`, le gabarit
retombe sur `old_html` — réservé aux vieux articles migrés.)

### 5. Liens internes (1 à 4 par article)

- Insérer **1 à 4 liens internes** vers d'autres pages du site, dans `intro_html`,
  les `body_html` des items, le `verdict_html`, la FAQ ou les callouts.
- **Format article :** `<a href="/top5/{slug-cible}.htm">ancre descriptive</a>`
  (le slug doit exister dans `articles.json`).
- **Format univers :** `<a href="/univers/{slug-univers}/">…</a>` (ex.
  `/univers/argent-et-finance/`).
- Ancres **descriptives** (jamais « cliquez ici »), liens **pertinents** pour le lecteur, de
  préférence vers des articles du **même univers** ou complémentaires.

### 6. Photo — toujours une vraie photo OpenAI avant publication

**Règle absolue :** jamais publier un article sans visuel. Toujours **une vraie photo de
couverture générée par OpenAI, ultra réaliste**, « photo généraliste sur le thème », avant
publication — avec un traitement (lumière, ambiance) cohérent avec la **DA du site**
(fonds sombres `#0d0d11`, accent **lime électrique** `#d4ff3d`, rendu premium/éditorial).

**Modèle & paramètres** (OpenAI, clé depuis l'environnement — §3 des règles d'intervention) :

```json
{ "model": "gpt-image-2", "size": "1536x1024", "quality": "medium" }
```

- **Une seule image (hero) par article.** Pas de galerie, pas d'image dans le corps.
- Enregistrer le fichier dans **`src/assets/posts/{slug}.jpg`** et renseigner le champ
  `image` de l'article avec **ce nom de fichier** (Astro l'optimise au build).
- Prompt type : *« Photo ultra réaliste, généraliste sur le thème “{sujet}”, éclairage
  premium éditorial, ambiance sombre avec touche lumineuse lime, format paysage »* — adapter
  au sujet.

---

## Publier un nouvel article — checklist

1. **Anti-cannibalisation** : lire l'existant, choisir un sujet/angle neuf (§3).
2. **Rédiger** l'objet `content` complet en français, qualité maximale (§4), avec **1–4
   liens internes** (§5).
3. **Générer la photo** hero via OpenAI `gpt-image-2` (1536×1024, `quality: medium`) →
   `src/assets/posts/{slug}.jpg` (§6).
4. **Ajouter l'article** dans `src/data/articles.json` → tableau `articles` :
   - `id` : nouvel entier **unique ≥ 100000** (articles rédigés par Claude ; incrémenter
     depuis le max existant — dernier utilisé : `100002`).
   - `slug` unique et stable, `title`, `date`/`modified` au format `YYYY-MM-DDTHH:MM:SS`,
     `image` = nom de fichier, `univers` (§1), `excerpt` (texte brut ≤ 220 car.),
     `old_html: ""`, `content` (l'objet du §4).
   - Le tri d'affichage se fait par `date` (récent d'abord).
5. **Valider en local** : `npm run build` (doit passer sans erreur).
6. **Commit + push sur `main`** (Règle n°1), message clair (ex. « Ajoute l'article TOP 5 :
   … »).

---

## Développement

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # génère dist/ (+ postbuild) — à lancer avant tout push
npm run preview  # prévisualise dist/
```
