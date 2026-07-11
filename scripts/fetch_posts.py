#!/usr/bin/env python3
"""Récupère titres, slugs, images à la une et ancien contenu depuis l'API REST
WordPress de acetic.fr -> scripts/wp_posts.json"""
import json, os, urllib.request, urllib.error

BASE = "https://www.acetic.fr/wp-json/wp/v2"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_all(endpoint):
    out, page = [], 1
    while True:
        try:
            data = get(f"{BASE}/{endpoint}?per_page=100&page={page}")
        except urllib.error.HTTPError as e:
            if e.code == 400:
                break
            raise
        if not data:
            break
        out.extend(data)
        page += 1
    return out


def main():
    cats = {c["id"]: c for c in fetch_all("categories")}
    tags = {t["id"]: t for t in fetch_all("tags")}
    posts, page = [], 1
    while True:
        try:
            data = get(f"{BASE}/posts?per_page=20&page={page}&_embed=1")
        except urllib.error.HTTPError as e:
            if e.code == 400:
                break
            raise
        if not data:
            break
        for p in data:
            fm = None
            media = p.get("_embedded", {}).get("wp:featuredmedia", [])
            if media and isinstance(media, list) and media[0].get("source_url"):
                fm = media[0]["source_url"]
            posts.append({
                "id": p["id"], "slug": p["slug"], "title": p["title"]["rendered"],
                "link": p["link"], "date": p["date"], "modified": p["modified"],
                "featured_media_id": p.get("featured_media"), "featured_image": fm,
                "categories": [cats.get(c, {}).get("name") for c in p.get("categories", [])],
                "tags": [tags.get(t, {}).get("name") for t in p.get("tags", [])],
                "excerpt_raw": p.get("excerpt", {}).get("rendered", ""),
                "content_html": p.get("content", {}).get("rendered", ""),
            })
        page += 1
    out = {"count": len(posts), "posts": posts}
    with open(os.path.join(ROOT, "scripts", "wp_posts.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"{len(posts)} articles récupérés ({sum(1 for p in posts if p['featured_image'])} avec image)")


if __name__ == "__main__":
    main()
