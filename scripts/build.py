"""Builds the profile's typographic SVGs in assets/ (dark + light).

Monochrome, transparent backgrounds, one font stack. The only motion is the
headline easing up once; every SVG is fully readable with animation off.
Live numbers (contributions) come from the GitHub API so the daily workflow
keeps the stats line current. Standard library only.
"""
import base64
import json
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "OjasMishra32"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
MEDIA = os.path.join(ROOT, "media")

FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(fg="#f5f5f7", gray="#a1a1a6"),
    "light": dict(fg="#1d1d1f", gray="#6e6e73"),
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar { totalContributions } }
  }
}"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def x(s):
    return escape(str(s))


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def svg(W, H, label, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{x(label)}">\n'
            f'<style>{style}\n@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}</style>\n'
            f'{body}\n</svg>\n')


def text(x0, y, s, size, fill, weight=400, ls=0, anchor="middle", cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text{c} x="{x0}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{ls}" fill="{fill}">{x(s)}</text>')


# The headline eases up once. Only position moves, never opacity, so a
# viewer that freezes the first frame still shows it.
RISE = """
.rise { animation: rise 1.2s cubic-bezier(.2,.7,.2,1) both; }
.rise2 { animation: rise 1.2s cubic-bezier(.2,.7,.2,1) .15s both; }
@keyframes rise { from { transform: translateY(12px); } to { transform: none; } }
"""


def hero(c):
    W, H = 1200, 330
    body = (text(600, 150, "Ojasva Mishra", 116, c["fg"], 700, -4, cls="rise")
            + text(600, 232, "Software engineer at Northrop Grumman.", 34, c["gray"], 500, -.4, cls="rise2")
            + text(600, 278, "Computer Engineering and Finance at the University of Florida.", 34, c["gray"], 500, -.4, cls="rise2"))
    return svg(W, H, "Ojasva Mishra. Software engineer at Northrop Grumman. Computer Engineering and Finance at the University of Florida.", body, RISE)


def title(c, name, line, W=1200):
    H = 150 if line else 100
    body = text(W / 2, 70, name, 62, c["fg"], 700, -1.8)
    if line:
        body += text(W / 2, 124, line, 30, c["gray"], 500, -.3)
    return svg(W, H, f"{name}. {line}" if line else name, body)


def stats(c, u):
    contrib = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    s = f"3 first-author papers  ·  1,000+ Twinly users  ·  {contrib:,} contributions this year"
    return svg(1200, 60, s, text(600, 38, s, 24, c["gray"], 500, -.2))


def photo(path, label, radius=28, crop=None):
    """Embeds a real project image with rounded corners (one file for both themes)."""
    import struct
    with open(path, "rb") as f:
        data = f.read()
    # JPEG size from the SOF marker
    i, w, h = 2, 0, 0
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            break
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    b64 = base64.b64encode(data).decode()
    cx, cy, cw, ch = crop or (0, 0, w, h)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{cw}" height="{ch}" viewBox="{cx} {cy} {cw} {ch}" role="img" aria-label="{x(label)}">'
            f'<defs><clipPath id="r"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="{radius * cw / 1200:.0f}"/></clipPath></defs>'
            f'<image clip-path="url(#r)" width="{w}" height="{h}" href="data:image/jpeg;base64,{b64}" xlink:href="data:image/jpeg;base64,{b64}"/></svg>\n')


SECTIONS = {
    "applytwin": ("ApplyTwin", "Your job search, on autopilot. Free and open source."),
    "courtside": ("Courtside", "Calls the point a median 162 ms before the bounce."),
    "dejaview": ("Déjà View", "Photos of any space, turned into a world you walk into."),
    "experience": ("Experience", ""),
    "research": ("Research", ""),
    "more": ("Also built", ""),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    u = fetch()
    for t, c in THEMES.items():
        write(f"hero-{t}.svg", hero(c))
        write(f"stats-{t}.svg", stats(c, u))
        for key, (name, line) in SECTIONS.items():
            write(f"t-{key}-{t}.svg", title(c, name, line))
    write("photo-courtside.svg", photo(os.path.join(MEDIA, "courtside.jpg"), "Courtside: the tracker following the ball through a real tennis rally, with court lines fitted per frame.", crop=(0, 90, 636, 600)))
    write("photo-dejaview.svg", photo(os.path.join(MEDIA, "dejaview.jpg"), "Deja View: a room reconstructed as a walkable 3D scene in the browser."))
    print("built", len(os.listdir(OUT)), "files")


if __name__ == "__main__":
    main()
