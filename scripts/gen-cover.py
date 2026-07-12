#!/usr/bin/env python3
"""Génère la couverture de l'article 'doublons d'assurance' aux couleurs du site."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersampling
W, H = 1536 * S, 1024 * S

BG_TOP   = (13, 13, 17)
BG_BOT   = (9, 9, 12)
SURFACE  = (26, 26, 33)
SURFACE2 = (34, 34, 43)
LIME     = (212, 255, 61)
TEXT     = (245, 245, 247)
DIM      = (166, 166, 178)
GOOD     = (74, 222, 128)

def font(path, size):
    return ImageFont.truetype(path, size * S)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

img = Image.new("RGB", (W, H), BG_TOP)

# --- fond dégradé vertical ---
top = Image.new("RGB", (1, H))
for y in range(H):
    t = y / H
    top.putpixel((0, y), tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
img = top.resize((W, H))

draw = ImageDraw.Draw(img, "RGBA")

# --- halo lime en haut à droite ---
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
gd.ellipse([W * 0.55, -H * 0.35, W * 1.2, H * 0.6], fill=90)
glow = glow.filter(ImageFilter.GaussianBlur(160 * S))
lime_layer = Image.new("RGB", (W, H), LIME)
img = Image.composite(lime_layer, img, glow.point(lambda p: int(p * 0.28)))
draw = ImageDraw.Draw(img, "RGBA")

# --- grille de points discrète ---
for gx in range(0, W, 46 * S):
    for gy in range(0, H, 46 * S):
        draw.ellipse([gx, gy, gx + 2 * S, gy + 2 * S], fill=(255, 255, 255, 10))

def card(cx, cy, w, h, fill, border=(255, 255, 255, 26), r=26, shadow=True):
    x0, y0 = cx - w // 2, cy - h // 2
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([x0, y0 + 14 * S, x0 + w, y0 + h + 14 * S], r * S, fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(26 * S))
        img.paste(sh, (0, 0), sh)
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], r * S, fill=fill, outline=border, width=2 * S)
    return x0, y0

# --- deck de contrats (3 cartes en éventail) ---
cx, cy = int(W * 0.40), int(H * 0.52)
card(cx + 60 * S, cy - 6 * S, 430 * S, 560 * S, (22, 22, 28, 255), r=24)
card(cx + 28 * S, cy + 10 * S, 430 * S, 560 * S, (28, 28, 36, 255), r=24)
x0, y0 = card(cx - 12 * S, cy + 26 * S, 430 * S, 560 * S, SURFACE + (255,), r=24)

# entête de la carte de devant
pad = 34 * S
draw.rounded_rectangle([x0 + pad, y0 + pad, x0 + pad + 150 * S, y0 + pad + 26 * S], 8 * S, fill=(LIME + (60,)))
draw.text((x0 + pad, y0 + pad + 44 * S), "CONTRAT", font=font(FB, 15), fill=DIM)

# lignes de "texte" + 2 lignes en double surlignées
rows_y = y0 + pad + 92 * S
line_h = 58 * S
dup_idx = {1, 3}
dup_pts = []
for i in range(6):
    ry = rows_y + i * line_h
    if i in dup_idx:
        draw.rounded_rectangle([x0 + pad - 8 * S, ry - 12 * S, x0 + 430 * S - pad + 8 * S, ry + 24 * S],
                               9 * S, fill=(LIME + (34,)), outline=(LIME + (140,)), width=2 * S)
        draw.line([x0 + pad, ry + 6 * S, x0 + 300 * S, ry + 6 * S], fill=LIME, width=6 * S)
        draw.line([x0 + 315 * S, ry + 6 * S, x0 + 360 * S, ry + 6 * S], fill=(LIME + (150,)), width=6 * S)
        dup_pts.append((x0 + 430 * S - pad + 8 * S, ry + 6 * S))
    else:
        w2 = [340, 260, 300, 220, 310, 250][i] * S
        draw.line([x0 + pad, ry + 6 * S, x0 + pad + w2, ry + 6 * S], fill=(255, 255, 255, 40), width=6 * S)

# accolade lime reliant les deux doublons + badge ×2
if len(dup_pts) == 2:
    bx = dup_pts[0][0] + 26 * S
    draw.line([dup_pts[0][0] + 6 * S, dup_pts[0][1], bx, dup_pts[0][1]], fill=LIME, width=4 * S)
    draw.line([dup_pts[1][0] + 6 * S, dup_pts[1][1], bx, dup_pts[1][1]], fill=LIME, width=4 * S)
    draw.line([bx, dup_pts[0][1], bx, dup_pts[1][1]], fill=LIME, width=4 * S)
    midy = (dup_pts[0][1] + dup_pts[1][1]) // 2
    draw.ellipse([bx + 10 * S, midy - 26 * S, bx + 72 * S, midy + 26 * S], fill=LIME)
    draw.text((bx + 24 * S, midy - 20 * S), "×2", font=font(FB, 22), fill=(9, 9, 12))

# --- loupe qui inspecte le contrat ---
lx, ly, lr = int(W * 0.60), int(H * 0.44), 132 * S
draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(212, 255, 61, 22), outline=LIME, width=14 * S)
# reflet
draw.arc([lx - lr + 26 * S, ly - lr + 26 * S, lx + lr - 70 * S, ly + lr - 70 * S], 150, 250, fill=(255, 255, 255, 90), width=6 * S)
# euro dans la loupe
ef = font(FB, 96)
eb = draw.textbbox((0, 0), "€", font=ef)
draw.text((lx - (eb[2] - eb[0]) / 2, ly - (eb[3] - eb[1]) / 2 - eb[1]), "€", font=ef, fill=LIME)
# manche
import math
ang = math.radians(45)
hx, hy = lx + int(lr * math.cos(ang)), ly + int(lr * math.sin(ang))
draw.line([hx, hy, hx + 118 * S, hy + 118 * S], fill=LIME, width=30 * S)
draw.ellipse([hx + 100 * S, hy + 100 * S, hx + 150 * S, hy + 150 * S], fill=LIME)

# --- textes ---
# pastille marque
by = int(H * 0.075)
draw.ellipse([90 * S, by, 108 * S, by + 18 * S], fill=LIME)
draw.text((122 * S, by - 4 * S), "ACETIC  ·  LE MÉDIA DES TOP 5", font=font(FB, 17), fill=DIM)

# eyebrow univers
ey = int(H * 0.70)
draw.text((90 * S, ey), "ARGENT & FINANCE", font=font(FB, 20), fill=LIME)
# titre graphique
draw.text((88 * S, ey + 40 * S), "Doublons d’assurance :", font=font(FB, 52), fill=TEXT)
draw.text((88 * S, ey + 104 * S), "l’audit qui allège la facture", font=font(FR, 40), fill=DIM)

# liseré lime en bas
draw.rectangle([0, H - 10 * S, W, H], fill=LIME)

out = img.resize((1536, 1024), Image.LANCZOS).convert("RGB")
out.save("src/assets/posts/top-5-methodes-reperer-doublons-assurance-reduire-cotisations.jpg",
         quality=90, optimize=True, progressive=True)
print("cover written")
