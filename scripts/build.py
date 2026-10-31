"""Builds the profile's section titles in assets/ (dark + light SVGs).

Transparent, one font stack, a wide and a narrow (phone) layout in each
file. The contributions title reads the live count from the GitHub API so
the daily workflow keeps it current. The 3D renders live in render/.
Standard library only.
"""
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


# Every SVG carries a wide and a narrow layout. On a phone the README
# column is ~300px wide, so the narrow one uses larger type and more lines.
SWAP = """
.n { display: none; }
@media (max-width: 700px) { .w { display: none; } .n { display: inline; } }
"""


def split2(s):
    words = s.split()
    best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
    return " ".join(words[:best]), " ".join(words[best:])


def title(c, name, line, W=1200):
    if not line:
        body = f'<g class="w">{text(W / 2, 74, name, 62, c["fg"], 700, -1.8)}</g><g class="n">{text(W / 2, 104, name, 112, c["fg"], 700, -3)}</g>'
        return svg(W, 130, name, body, SWAP)
    a, b = split2(line)
    wide = text(W / 2, 150, name, 62, c["fg"], 700, -1.8) + text(W / 2, 206, line, 30, c["gray"], 500, -.3)
    narrow = (text(W / 2, 104, name, 112, c["fg"], 700, -3)
              + text(W / 2, 190, a, 60, c["gray"], 500, -.8) + text(W / 2, 262, b, 60, c["gray"], 500, -.8))
    return svg(W, 290, f"{name}. {line}", f'<g class="w">{wide}</g><g class="n">{narrow}</g>', SWAP)


SECTIONS = {
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
    n = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    for t, c in THEMES.items():
        for key, (name, line) in SECTIONS.items():
            write(f"t-{key}-{t}.svg", title(c, name, line))
        write(f"t-contrib-{t}.svg", title(c, f"{n:,}", "contributions in the last year"))
    print("built", len(os.listdir(OUT)), "files")


if __name__ == "__main__":
    main()
