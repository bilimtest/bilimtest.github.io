#!/usr/bin/env python3
"""PDF mock testdan har bir topşiriqni alohida PNG qilib qirqadi.

Foydalaniş:
    python3 crop_questions.py test.pdf out_dir [--match-page N] [--dpi 140] [--num-xmax 110]

Talablar: poppler-utils (pdftoppm, pdftotext), Pillow.
Topşiriq raqamlari çap çetda "1." "2." ... körinişida bölishi kerak.
--match-page: 33–35 moslaştiriş bloki turgan sahifa (butun sahifa bitta rasm bölib qirqiladi).

Algoritm (index.html dagi brauzer varianti ham xuddi şunday, `cropPdf()`):
  1. Har sahifada raqamlarni ketma-ket qidiramiz ("1.", "2.", ... x < num-xmax).
  2. Ikki topşiriq çegarasi: oldingi topşiriq matni tugagan joy bilan keyingi raqam orasidagi
     eng uzun "siyohsiz" piksel qatorlari oraliğining örtasi. Şunda formula çiziqlari
     (ildiz belgisining yuqori çizigi, kasr) qo'şni rasmga tuşib qolmaydi.
  3. Rasm siyoh bo'yiça qirqiladi; rangli suv belgisi siyoh hisoblanmaydi.
"""
import argparse, os, re, subprocess, tempfile
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("out")
ap.add_argument("--match-page", type=int, default=0)
ap.add_argument("--dpi", type=int, default=140)
ap.add_argument("--num-xmax", type=float, default=110, help="raqam turadigan çap çet chegarasi (pt)")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
S = a.dpi / 72
INK = 150  # piksel siyoh: R, G, B uçalasi ham INK dan kiçik (qora/kulrang)
tmp = tempfile.mkdtemp()
subprocess.run(["pdftotext", "-bbox-layout", a.pdf, f"{tmp}/b.html"], check=True)
subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", a.pdf, f"{tmp}/p"], check=True)
pages = open(f"{tmp}/b.html", encoding="utf8").read().split("<page ")[1:]
pngs = sorted(f for f in os.listdir(tmp) if f.startswith("p-"))

_imgs = {}
def page_img(pi):
    if pi not in _imgs:
        _imgs[pi] = Image.open(f"{tmp}/{pngs[pi-1]}").convert("RGB")
    return _imgs[pi]

def ink_mask(im):
    r, g, b = [ch.point(lambda v: 255 if v < INK else 0) for ch in im.split()]
    from PIL import ImageChops
    return ImageChops.multiply(ImageChops.multiply(r, g), b)

def cut_between(pi, x0, x1, top, bottom):
    """top..bottom (pt) orasidagi eng uzun siyohsiz qatorlar oraliğining örtasi (pt)."""
    if bottom - top < 1:
        return (top + bottom) / 2
    im = page_img(pi)
    m = ink_mask(im.crop((int(x0*S), int(top*S), int(x1*S), int(bottom*S))))
    w, h = m.size
    px = m.load()
    best_s, best_n, run, rs = 0, 0, 0, 0
    for y in range(h + 1):
        ink = y == h or any(px[x, y] for x in range(w))
        if not ink:
            if run == 0: rs = y
            run += 1
        else:
            if run > best_n: best_s, best_n = rs, run
            run = 0
    if best_n == 0:
        return bottom
    return top + (best_s + best_n / 2) / S

def crop(pi, x0, x1, y0, y1, name):
    c = page_img(pi).crop((int(x0*S), int(y0*S), int(x1*S), int(y1*S)))
    bb = ink_mask(c).getbbox()
    if bb:
        p = 10
        c = c.crop((max(0, bb[0]-p), max(0, bb[1]-p), min(c.width, bb[2]+p), min(c.height, bb[3]+p)))
    c.save(f"{a.out}/{name}.png", optimize=True)

expected = 1
for pi, p in enumerate(pages, 1):
    words = [(float(x0), float(y0), float(x1), float(y1), w) for x0, y0, x1, y1, w in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', p)]
    if not words: continue
    foot = min([y0 for x0, y0, x1, y1, w in words if y0 > 760] or [835])
    body = [w for w in words if 50 < w[1] and w[3] < foot - 3]
    if not body: continue
    X0 = max(0, min(w[0] for w in body) - 8); X1 = min(595, max(w[2] for w in body) + 8)
    if pi == a.match_page:
        crop(pi, X0, X1, min(w[1] for w in body) - 6, max(w[3] for w in body) + 6, "q33")
        expected = 36; continue
    nums = []
    for x0, y0, x1, y1, w in words:
        if re.fullmatch(r"\d{1,2}\.", w) and x0 < a.num_xmax and int(w[:-1]) == expected:
            nums.append((expected, y0)); expected += 1
    if not nums: continue
    dq = sorted(y0 for x0, y0, x1, y1, w in words if w.startswith("Diqqat"))
    bottom = max(w[3] for w in body) + 6
    cuts = []
    for i, (n, y0) in enumerate(nums):
        if i + 1 < len(nums):
            ny = nums[i+1][1]
            above = [w[3] for w in body if y0 <= w[1] and w[3] < ny - 1]
            top = max(above) if above else y0
            cuts.append(cut_between(pi, X0, X1, top, ny))
        else:
            cuts.append(bottom)
    for i, (n, y0) in enumerate(nums):
        if i > 0:
            start = cuts[i-1]
        else:  # sahifadagi birinçi topşiriq: yuqoridagi sarlavha yoki böşliq bilan çegarala
            above = [w[3] for w in words if 40 < w[1] and w[3] < y0 - 1]
            start = cut_between(pi, X0, X1, max(above) if above else max(40, y0 - 30), y0)
        y1 = cuts[i]
        ds = [d for d in dq if y0 < d < y1 + 8]
        if ds: y1 = min(y1, ds[0] - 6)
        crop(pi, X0, X1, start, y1, f"q{n:02d}")
print("tayyor:", sorted(os.listdir(a.out)))
