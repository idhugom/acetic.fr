import json, os, urllib.request, urllib.error, hashlib

d=json.load(open("scripts/wp_posts.json"))
os.makedirs("public/images/posts",exist_ok=True)
manifest={}
ok=0; fail=0
for p in d["posts"]:
    url=p["featured_image"]
    if not url: continue
    ext=os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
    if ext not in (".jpg",".jpeg",".png",".webp",".avif"): ext=".jpg"
    fn=f"{p['slug']}{ext}"
    out=f"public/images/posts/{fn}"
    manifest[p["id"]]=f"/images/posts/{fn}"
    if os.path.exists(out) and os.path.getsize(out)>1000:
        ok+=1; continue
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=60) as r:
            data=r.read()
        open(out,"wb").write(data)
        ok+=1
    except Exception as e:
        print("FAIL",p["slug"],e); fail+=1
json.dump(manifest,open("scripts/image_manifest.json","w"))
print("downloaded ok:",ok,"fail:",fail)
