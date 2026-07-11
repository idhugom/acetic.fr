#!/usr/bin/env python3
"""Construit le JSONL de tâches et lance le Batch API OpenAI (Responses API,
gpt-5.6-terra, sortie structurée). Écrit l'id du batch dans scripts/.batch_id.
Requiert OPENAI_API_KEY."""
import json, os, sys, urllib.request, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_common as gc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = os.environ["OPENAI_API_KEY"]


def build_jsonl():
    wp = json.load(open(os.path.join(ROOT, "scripts", "wp_posts.json"), encoding="utf-8"))
    path = os.path.join(ROOT, "scripts", "batch_input.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for p in wp["posts"]:
            body = gc.build_body(p["title"], p["content_html"])
            f.write(json.dumps({"custom_id": f"post-{p['id']}", "method": "POST",
                                "url": "/v1/responses", "body": body}, ensure_ascii=False) + "\n")
    print("JSONL:", len(wp["posts"]), "tâches")
    return path


def upload(path):
    out = subprocess.check_output(["curl", "-sS", "https://api.openai.com/v1/files",
        "-H", f"Authorization: Bearer {KEY}", "-F", "purpose=batch", "-F", f"file=@{path}"])
    return json.loads(out)["id"]


def create_batch(file_id):
    body = json.dumps({"input_file_id": file_id, "endpoint": "/v1/responses",
                       "completion_window": "24h", "metadata": {"project": "acetic-top5"}}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/batches", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    path = build_jsonl()
    fid = upload(path)
    print("file:", fid)
    b = create_batch(fid)
    print("batch:", b["id"], "status:", b["status"])
    open(os.path.join(ROOT, "scripts", ".batch_id"), "w").write(b["id"])


if __name__ == "__main__":
    main()
