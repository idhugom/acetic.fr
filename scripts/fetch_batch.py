#!/usr/bin/env python3
"""Vérifie l'état du Batch API et, s'il est terminé, télécharge la sortie dans
scripts/batch_output.jsonl. Requiert OPENAI_API_KEY.
Usage: python scripts/fetch_batch.py [batch_id]"""
import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = os.environ["OPENAI_API_KEY"]


def api(path):
    req = urllib.request.Request(f"https://api.openai.com/v1{path}",
        headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    bid = sys.argv[1] if len(sys.argv) > 1 else open(os.path.join(ROOT, "scripts", ".batch_id")).read().strip()
    b = json.loads(api(f"/batches/{bid}"))
    print("status:", b["status"], "counts:", b.get("request_counts"))
    if b["status"] != "completed":
        print("Batch pas encore terminé.")
        return 1
    data = api(f"/files/{b['output_file_id']}/content")
    with open(os.path.join(ROOT, "scripts", "batch_output.jsonl"), "wb") as f:
        f.write(data)
    print("Sortie écrite dans scripts/batch_output.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
