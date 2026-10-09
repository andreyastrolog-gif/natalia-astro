#!/usr/bin/env python3
"""Publish one post to all targets: Telegram (@astroyogaN) + site blog, then git commit/push.
Usage: TG_NATALIA_BOT_TOKEN=... publish.py --caption caption.html --image pic.png [--title T] [--slug S] [--targets telegram,blog] [--no-push]
Add new networks (TikTok, Facebook...) by writing a function target_<name>(post) and registering it in TARGETS."""
import argparse, datetime, html, json, os, re, shutil, subprocess, sys, urllib.request, uuid
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://andreyastrolog-gif.github.io/natalia-astro/"
SRC = os.path.join(ROOT, "content", "blog", "posts.json")
CHANNEL = "@astroyogaN"

def load():
    return json.load(open(SRC, encoding="utf-8")) if os.path.exists(SRC) else []

def text_of(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h))

def slugify(s):
    tr = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", ["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","ts","ch","sh","sch","","y","","e","yu","ya"]))
    s = "".join(tr.get(c, c) for c in s.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or uuid.uuid4().hex[:8]

def target_telegram(post):
    tok = os.environ["TG_NATALIA_BOT_TOKEN"]
    b = "----" + uuid.uuid4().hex
    img = open(post["image_path"], "rb").read()
    parts = []
    for k, v in (("chat_id", CHANNEL), ("caption", post["caption"]), ("parse_mode", "HTML")):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="photo"; filename="{os.path.basename(post["image_path"])}"\r\nContent-Type: image/png\r\n\r\n'.encode() + img + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendPhoto", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    if not r.get("ok"): raise RuntimeError(r)
    post.setdefault("links", {})["telegram"] = f"https://t.me/{CHANNEL[1:]}/{r['result']['message_id']}"

def target_blog(post):
    ext = os.path.splitext(post["image_path"])[1]
    dst = os.path.join(ROOT, "blog", "img", post["slug"] + ext)
    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copyfile(post["image_path"], dst)
    post["image"] = "img/" + post["slug"] + ext
    post.setdefault("links", {})["blog"] = SITE + "blog/" + post["slug"] + "/"

TARGETS = {"telegram": target_telegram, "blog": target_blog}   # add "tiktok": target_tiktok later

HEAD = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{url}">
<meta property="og:type" content="{ogt}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml"><link rel="icon" href="{r}favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="{r}apple-touch-icon.png"><link rel="manifest" href="{r}site.webmanifest"><meta name="theme-color" content="#faf7f2">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="{r}css/style.css">
<style>.bw{{max-width:820px;margin:0 auto;padding:120px 5vw 80px}}.bl{{display:grid;gap:28px}}.bc{{display:grid;grid-template-columns:200px 1fr;gap:22px;background:#fff;border-radius:var(--r);overflow:hidden;text-decoration:none;box-shadow:0 6px 24px #0000000a}}.bc img{{height:100%;object-fit:cover}}.bc div{{padding:18px 18px 18px 0}}.bm{{color:var(--mute);font-size:.85rem}}.bp img{{border-radius:var(--r);margin:24px 0}}.bp .tx{{white-space:pre-line}}.bp .tx a{{color:var(--gold)}}@media(max-width:600px){{.bc{{grid-template-columns:1fr}}.bc div{{padding:0 18px 18px}}}}</style>{ld}</head><body>
<header class="hdr scrolled"><a class="logo" href="{r}">Наталья<span>·</span>Джйотиш</a><nav class="nav" style="display:flex;gap:22px;align-items:center"><a href="{r}#about">Обо мне</a><a href="{r}blog/">Блог</a><a class="btn btn-sm" href="https://t.me/astroyogaN" target="_blank" rel="noopener">Записаться</a></nav></header><main class="bw">"""
FOOT = '</main><footer style="text-align:center;padding:30px;color:var(--mute)">© Наталья · ведический астролог · <a href="https://t.me/astroyogaN">Telegram</a></footer></body></html>'

def build(posts):
    e = html.escape
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)
    cards = "".join(f'<a class="bc" href="{p["slug"]}/"><img src="{p["image"]}" alt="{e(p["title"])}" loading="lazy"><div><p class="bm">{p["date"]}</p><h3>{e(p["title"])}</h3><p>{e(p["excerpt"])}</p></div></a>' for p in posts)
    idx = HEAD.format(title="Блог — Наталья, ведический астролог", desc="Лунный календарь, накшатры и советы ведической астрологии от Натальи.", url=SITE+"blog/", ogt="website", img=SITE+"img/og.jpg", r="../", ld="")
    open(os.path.join(ROOT, "blog", "index.html"), "w", encoding="utf-8").write(idx + '<p class="eyebrow">Блог</p><h1>Заметки астролога</h1><div class="bl" style="margin-top:40px">' + cards + "</div>" + FOOT)
    for p in posts:
        d = os.path.join(ROOT, "blog", p["slug"]); os.makedirs(d, exist_ok=True)
        url = SITE + "blog/" + p["slug"] + "/"
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"], "image": SITE+"blog/"+p["image"], "author": {"@type": "Person", "name": "Наталья"}, "mainEntityOfPage": url}, ensure_ascii=False) + "</script>"
        body = p["caption"].replace("\n", "<br>\n")
        h = HEAD.format(title=e(p["title"]) + " — блог Натальи", desc=e(p["excerpt"]), url=url, ogt="article", img=SITE+"blog/"+p["image"], r="../../", ld=ld)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(h + f'<article class="bp"><p class="bm">{p["date"]} · <a href="../">← все записи</a></p><h1>{e(p["title"])}</h1><img src="../{p["image"]}" alt="{e(p["title"])}"><div>{body}</div></article>' + FOOT)
    urls = [(SITE, posts[0]["date"] if posts else datetime.date.today().isoformat()), (SITE+"blog/", posts[0]["date"] if posts else "")] + [(SITE+"blog/"+p["slug"]+"/", p["date"]) for p in posts]
    open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls) + "</urlset>\n")

def main():
    a = argparse.ArgumentParser(); a.add_argument("--caption"); a.add_argument("--image"); a.add_argument("--title"); a.add_argument("--slug")
    a.add_argument("--targets", default="telegram,blog"); a.add_argument("--no-push", action="store_true"); a.add_argument("--rebuild-only", action="store_true")
    o = a.parse_args(); posts = load()
    if not o.rebuild_only:
        cap = open(o.caption, encoding="utf-8").read().strip()
        if len(text_of(cap)) > 1024: sys.exit(f"caption too long: {len(text_of(cap))} > 1024")
        lines = [l for l in text_of(cap).splitlines() if l.strip()]
        title = o.title or re.sub(r"^\W+", "", lines[0]).strip()
        post = {"date": datetime.date.today().isoformat(), "title": title, "slug": o.slug or slugify(title), "caption": cap,
                "excerpt": " ".join(lines[1:4])[:200], "image_path": os.path.abspath(o.image)}
        for t in o.targets.split(","): TARGETS[t.strip()](post); print(t, "ok", post.get("links", {}).get(t, ""))
        post.pop("image_path"); posts = [p for p in posts if p["slug"] != post["slug"]] + [post]
        os.makedirs(os.path.dirname(SRC), exist_ok=True); json.dump(posts, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    build(posts)
    if not o.no_push:
        subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
        subprocess.run(["git", "-C", ROOT, "commit", "-qm", "blog: " + (posts[-1]["title"] if posts else "rebuild")], check=False)
        subprocess.run(["git", "-C", ROOT, "push", "-q"], check=True)
if __name__ == "__main__": main()
