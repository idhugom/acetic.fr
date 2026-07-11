"""Shared content-generation logic: JSON schema + prompt builder for gpt-5.6-terra."""
import re, html

UNIVERS = [
    "Tech & Numérique",
    "Argent & Finance",
    "Bien-être & Santé",
    "Maison & Déco",
    "Food & Cuisine",
    "Voyage & Loisirs",
    "Mode & Style",
    "Auto & Mobilité",
    "Animaux",
    "Éducation & Carrière",
    "Culture & Divertissement",
    "Famille & Enfants",
]

# ---- JSON schema for OpenAI structured output (strict) ----
def article_schema():
    def s(**k):
        return k
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "meta_title", "meta_description", "hook", "univers", "reading_time_min",
            "intro_html", "quick_answer", "criteria", "items", "comparison",
            "callouts", "faq", "verdict_html", "methodology_html", "keywords",
        ],
        "properties": {
            "meta_title": {"type": "string", "description": "SEO title, 45-62 chars, includes the topic."},
            "meta_description": {"type": "string", "description": "SEO meta description, 140-160 chars, engaging."},
            "hook": {"type": "string", "description": "Sous-titre punchy d'une phrase."},
            "univers": {"type": "string", "enum": UNIVERS},
            "reading_time_min": {"type": "integer"},
            "keywords": {"type": "array", "items": {"type": "string"}, "description": "5-8 mots-clés SEO."},
            "intro_html": {"type": "string", "description": "Intro engageante en HTML (2-3 <p>), qui pose l'intention de recherche."},
            "quick_answer": {
                "type": "object", "additionalProperties": False,
                "required": ["summary_html", "winner", "winner_reason"],
                "properties": {
                    "summary_html": {"type": "string", "description": "TL;DR type featured-snippet, HTML court."},
                    "winner": {"type": "string", "description": "Le grand gagnant (nom de l'item #1)."},
                    "winner_reason": {"type": "string", "description": "Pourquoi il gagne, 1 phrase."},
                },
            },
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["name", "why"],
                    "properties": {
                        "name": {"type": "string"},
                        "why": {"type": "string", "description": "Pourquoi ce critère compte."},
                    },
                },
                "description": "3-5 critères de classement.",
            },
            "items": {
                "type": "array",
                "description": "EXACTEMENT 5 éléments classés, du rang 1 (meilleur) au rang 5.",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["rank", "name", "tagline", "badge", "rating", "price_hint", "best_for", "body_html", "pros", "cons"],
                    "properties": {
                        "rank": {"type": "integer"},
                        "name": {"type": "string"},
                        "tagline": {"type": "string", "description": "Accroche courte sous le nom."},
                        "badge": {"type": "string", "description": "Ex: 'Meilleur choix', 'Meilleur rapport qualité-prix', 'Coup de cœur', 'Le plus polyvalent', 'Petit budget'."},
                        "rating": {"type": "number", "description": "Note /5, une décimale (ex 4.6)."},
                        "price_hint": {"type": "string", "description": "Indication de prix ou fourchette, ou '—' si non pertinent."},
                        "best_for": {"type": "string", "description": "Pour qui / quel usage."},
                        "body_html": {"type": "string", "description": "2-4 paragraphes HTML riches, concrets, sans blabla, avec détails utiles et actionnables."},
                        "pros": {"type": "array", "items": {"type": "string"}, "description": "3-4 avantages."},
                        "cons": {"type": "array", "items": {"type": "string"}, "description": "1-3 limites."},
                    },
                },
            },
            "comparison": {
                "type": "object", "additionalProperties": False,
                "required": ["title", "columns", "rows"],
                "properties": {
                    "title": {"type": "string"},
                    "columns": {"type": "array", "items": {"type": "string"}, "description": "1re colonne = 'Critère' puis une colonne par item (nom court)."},
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object", "additionalProperties": False,
                            "required": ["cells"],
                            "properties": {"cells": {"type": "array", "items": {"type": "string"}}},
                        },
                        "description": "Chaque ligne = un critère + sa valeur pour chaque item.",
                    },
                },
            },
            "callouts": {
                "type": "array",
                "description": "2-4 encarts de mise en avant d'information.",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["type", "title", "html"],
                    "properties": {
                        "type": {"type": "string", "enum": ["astuce", "info", "attention", "eco", "budget"]},
                        "title": {"type": "string"},
                        "html": {"type": "string"},
                    },
                },
            },
            "faq": {
                "type": "array",
                "description": "4-6 questions/réponses répondant aux intentions de recherche connexes.",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["question", "answer_html"],
                    "properties": {
                        "question": {"type": "string"},
                        "answer_html": {"type": "string"},
                    },
                },
            },
            "verdict_html": {"type": "string", "description": "Conclusion / verdict final, HTML, qui aide à décider."},
            "methodology_html": {"type": "string", "description": "Court paragraphe sur la méthodo de classement (transparence, E-E-A-T)."},
        },
    }


SYSTEM_PROMPT = """Tu es rédacteur en chef d'Acetic.fr, un média français 100% dédié aux CLASSEMENTS "TOP 5". \
Ta mission : produire l'article de référence sur son sujet — le plus complet, le plus utile et le plus agréable à lire du web francophone.

EXIGENCES DE QUALITÉ (non négociables) :
- Français impeccable, ton expert mais accessible, vivant, jamais générique ni "creux". Zéro remplissage.
- Réelle valeur ajoutée : conseils concrets, chiffres, ordres de grandeur, cas d'usage, pièges à éviter, critères de choix.
- Couvre TOUTES les intentions de recherche autour du sujet (comment choisir, pour qui, prix, alternatives, erreurs fréquentes).
- Structure TOP 5 stricte : exactement 5 éléments classés du meilleur (rang 1) au 5e, chacun avec un angle différencié.
- Contenu ORIGINAL et actualisé (nous sommes en 2026). Ne recopie pas l'ancien texte fourni : sers-t'en seulement pour connaître le sujet exact et les éléments attendus, puis fais bien mieux.
- Le tableau comparatif doit être réellement informatif (critères concrets comparés item par item).
- Les encarts mettent en avant une info à forte valeur (astuce d'expert, donnée clé, alerte, angle éco ou budget).
- FAQ : vraies questions que se posent les lecteurs, réponses précises et directes.
- N'invente pas de fausses données vérifiables trop précises (prix exacts, dates de sortie) : reste sur des fourchettes/ordres de grandeur crédibles quand tu n'es pas sûr.
- HTML des champs *_html : uniquement <p>, <ul>/<li>, <strong>, <em>, <a>. Pas de <h1>-<h6>, pas de style inline, pas de scripts.
- Écris comme pour un lecteur pressé qui veut décider vite ET un lecteur qui veut tout comprendre.

Réponds STRICTEMENT au format JSON demandé."""


def build_user_prompt(title, old_content_text):
    return f"""SUJET DE L'ARTICLE (titre exact à traiter) : « {title} »

Ancien contenu de référence (pour cadrer le sujet et les éléments attendus — À NE PAS RECOPIER, fais nettement mieux) :
\"\"\"
{old_content_text[:4000]}
\"\"\"

Rédige l'article TOP 5 de référence sur ce sujet, en respectant le schéma JSON. \
Choisis l'univers thématique le plus adapté. Vise un contenu long, complet et à forte valeur ajoutée."""


def html_to_text(h):
    h = re.sub(r"<[^>]+>", " ", h or "")
    h = html.unescape(h)
    return re.sub(r"\s+", " ", h).strip()


def build_body(title, old_content_html, batch=False):
    body = {
        "model": "gpt-5.6-terra",
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(title, html_to_text(old_content_html))},
        ],
        "reasoning": {"effort": "high"},
        "max_output_tokens": 30000,
        "text": {
            "verbosity": "high",
            "format": {
                "type": "json_schema",
                "name": "top5_article",
                "strict": True,
                "schema": article_schema(),
            },
        },
    }
    return body
