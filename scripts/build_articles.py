#!/usr/bin/env python3
"""
Fusionne :
  - scripts/wp_posts.json        (titre + slug + image + ancien contenu, source WordPress)
  - scripts/image_manifest.json  (id -> fichier image dans src/assets/posts)
  - scripts/batch_output.jsonl   (contenu régénéré par gpt-5.6-terra, si présent)
en un unique  src/data/articles.json  consommé par le site Astro.

Tant que le batch n'est pas terminé, on retombe proprement sur un contenu de
repli dérivé de l'ancien texte, pour que le site reste 100% fonctionnel.
"""
import json, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UNIVERS = [
    "Tech & Numérique", "Argent & Finance", "Bien-être & Santé", "Maison & Déco",
    "Food & Cuisine", "Voyage & Loisirs", "Mode & Style", "Auto & Mobilité",
    "Animaux", "Éducation & Carrière", "Culture & Divertissement", "Famille & Enfants",
]

# Heuristique de classement en univers (repli quand le contenu IA n'a pas encore d'univers).
KEYWORDS = {
    "Tech & Numérique": ["gadget", "smartphone", "windows", "application", "app", "informatique", "web", "cyber", "sécurité en ligne", "youtube", "surveillance", "caméra", "développement", "diplôme d", "vr", "réalité virtuelle", "jeux vidéo"],
    "Argent & Finance": ["budg", "crypto", "invest", "trading", "assurance", "facture", "énergie", "électricité", "portage", "banque", "fournisseur"],
    "Bien-être & Santé": ["yoga", "méditation", "fitness", "musculation", "santé", "thyroïde", "douleur", "mal de dos", "bouton", "cbd", "ambre", "voyance", "complément", "sommeil"],
    "Maison & Déco": ["nettoyage", "déco", "intérieur", "plante", "volet", "matelas", "garde", "meuble", "architect", "construction", "espace de vie", "montre en bois"],
    "Food & Cuisine": ["recette", "végétarien", "gaspillage", "pizza", "croquette", "aliment", "nourriture", "plat", "manger", "fête foraine"],
    "Voyage & Loisirs": ["voyage", "new york", "randonn", "plongée", "destination", "parc", "attraction", "zoo", "lille", "visiter", "endroit", "décalage horaire", "séjour"],
    "Mode & Style": ["mode", "chapeau", "casquette", "montre", "new balance", "chaine en or", "puff", "cigarette electronique", "style", "durable"],
    "Auto & Mobilité": ["4x4", "4×4", "auto", "trottinette", "voiture"],
    "Animaux": ["chien", "animaux", "animal", "chat", "froid"],
    "Éducation & Carrière": ["école", "commerce", "business", "carrière", "recrute", "ville", "productivité", "indépendant", "anglais", "prononcer", "mot", "cours en ligne", "sciences", "prénom", "développement personnel", "livre", "podcast", "créativité", "équilibrer vie"],
    "Culture & Divertissement": ["album", "métal", "musique", "film"],
    "Famille & Enfants": ["enfant", "famille", "baptême", "bébé", "vacances"],
}


def classify(title, cats):
    t = title.lower()
    best, score = "Culture & Divertissement", 0
    for u, kws in KEYWORDS.items():
        s = sum(1 for k in kws if k in t)
        if s > score:
            best, score = u, s
    return best if score else "Bien-être & Santé"


def strip_html(h):
    h = re.sub(r"<[^>]+>", " ", h or "")
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def load_batch():
    """Retourne {post_id(int): article_dict} depuis batch_output.jsonl si présent."""
    path = os.path.join(ROOT, "scripts", "batch_output.jsonl")
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        cid = rec.get("custom_id", "")
        m = re.match(r"post-(\d+)", cid)
        if not m:
            continue
        pid = int(m.group(1))
        resp = rec.get("response", {})
        if resp.get("status_code") not in (200, None):
            continue
        body = resp.get("body", {})
        # Responses API output extraction
        txt = ""
        for it in body.get("output", []):
            if it.get("type") == "message":
                for c in it.get("content", []):
                    if c.get("type") == "output_text":
                        txt += c.get("text", "")
        if not txt:
            # certaines réponses batch peuvent stocker directement output_text
            txt = body.get("output_text", "")
        if not txt:
            continue
        try:
            out[pid] = json.loads(txt)
        except Exception as e:
            print(f"  ! parse fail post {pid}: {e}", file=sys.stderr)
    return out


def fallback_content(post):
    """Contenu de repli minimal (avant l'arrivée du batch)."""
    return None  # None => le template affiche old_html


def main():
    wp = json.load(open(os.path.join(ROOT, "scripts", "wp_posts.json"), encoding="utf-8"))
    img = json.load(open(os.path.join(ROOT, "scripts", "image_manifest.json"), encoding="utf-8"))
    batch = load_batch()
    print(f"Articles IA disponibles : {len(batch)}/{len(wp['posts'])}")

    articles = []
    for p in wp["posts"]:
        pid = p["id"]
        content = batch.get(pid)
        univers = content["univers"] if (content and content.get("univers") in UNIVERS) else classify(p["title"], p.get("categories"))
        clean_title = html.unescape(p["title"])
        rec = {
            "id": pid,
            "slug": p["slug"],
            "title": clean_title,
            "date": p["date"],
            "modified": p["modified"],
            "image": img.get(str(pid)),
            "univers": univers,
            "excerpt": strip_html(p.get("excerpt_raw", ""))[:220],
            "old_html": p["content_html"],
            "content": content,  # riche (schéma) ou None
        }
        articles.append(rec)

    # tri: plus récents d'abord
    articles.sort(key=lambda a: a["date"], reverse=True)

    # comptage par univers
    counts = {}
    for a in articles:
        counts[a["univers"]] = counts.get(a["univers"], 0) + 1

    os.makedirs(os.path.join(ROOT, "src", "data"), exist_ok=True)
    out = {
        "generated_ratio": f"{len(batch)}/{len(articles)}",
        "univers": [{"name": u, "count": counts.get(u, 0)} for u in UNIVERS if counts.get(u, 0)],
        "articles": articles,
    }
    with open(os.path.join(ROOT, "src", "data", "articles.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("univers:", {k: v for k, v in sorted(counts.items(), key=lambda x: -x[1])})
    print(f"écrit src/data/articles.json ({len(articles)} articles, {len(batch)} enrichis IA)")


if __name__ == "__main__":
    main()
