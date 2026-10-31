"""Builds the profile SVGs in assets/ (dark + light variants).

Every SVG is readable with animation turned off: text never starts hidden,
and motion is limited to decorative shapes. Live numbers (stars,
contributions) come from the GitHub API so the daily workflow keeps them
current. Standard library only.
"""
import json
import math
import os
import random
import urllib.request
from xml.sax.saxutils import escape

USER = "OjasMishra32"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": dict(
        bg0="#070b14", bg1="#0d1117", card="#0d1117", card2="#111826", border="#263042",
        fg="#f0f6fc", muted="#9aa7b4", dim="#5b6675", grid="#1b2433",
        blue="#4c9dff", violet="#a78bfa", green="#3fdc8a", amber="#f5b14c", pink="#f472b6",
        glow=0.55,
    ),
    "light": dict(
        bg0="#f3f6fb", bg1="#ffffff", card="#ffffff", card2="#f6f8fa", border="#d0d7de",
        fg="#0f1720", muted="#4b5563", dim="#8b95a1", grid="#e3e8ef",
        blue="#0a64d6", violet="#7c3aed", green="#0f8a4f", amber="#b45309", pink="#be185d",
        glow=0.28,
    ),
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { name stargazerCount primaryLanguage { name color } }
    }
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


def svg_open(W, H, label, extra_style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{x(label)}">\n<style>{extra_style}\n'
            '@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }</style>\n')


# ------------------------------------------------------------------ hero
def hero(c):
    W, H = 1200, 440
    # Two-link arm on the right; shoulder and elbow sweep, the trail is the
    # end effector's path, precomputed so the static frame still shows it.
    bx, by, l1, l2 = 965, 368, 128, 104
    def fk(a1, a2):
        ex, ey = bx + l1 * math.cos(math.radians(a1)), by - l1 * math.sin(math.radians(a1))
        return ex, ey, ex + l2 * math.cos(math.radians(a1 + a2)), ey - l2 * math.sin(math.radians(a1 + a2))
    trail = []
    for k in range(121):
        t = k / 120 * 2 * math.pi
        a1 = 70 + 22 * math.sin(t)
        a2 = -55 + 30 * math.sin(t + 1.2)
        trail.append(fk(a1, a2)[2:])
    trail_d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in trail) + "Z"
    # keyframes for the arm, same motion as the trail
    n = 24
    a1s = [70 + 22 * math.sin(k / n * 2 * math.pi) for k in range(n + 1)]
    a2s = [-55 + 30 * math.sin(k / n * 2 * math.pi + 1.2) for k in range(n + 1)]
    sh = ";".join(f"{-a:.1f} {bx} {by}" for a in a1s)
    el = ";".join(f"{-a:.1f} {bx + l1} {by}" for a in a2s)
    a1, a2 = a1s[0], a2s[0]

    stars = "".join(
        f'<circle cx="{random.Random(i).uniform(20, W - 20):.0f}" cy="{random.Random(i * 7).uniform(20, H - 20):.0f}" '
        f'r="{random.Random(i * 3).uniform(.6, 1.6):.1f}" class="tw" style="animation-delay:{random.Random(i * 5).uniform(0, 6):.1f}s"/>'
        for i in range(70))

    grid = "".join(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}"/>' for gx in range(0, W + 1, 60)) + \
           "".join(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}"/>' for gy in range(20, H + 1, 60))

    style = f"""
.blob {{ animation: drift 18s ease-in-out infinite alternate; transform-origin: center; }}
.b2 {{ animation-duration: 23s; animation-direction: alternate-reverse; }}
.b3 {{ animation-duration: 29s; }}
@keyframes drift {{ 0% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(60px,-30px) scale(1.15); }} 100% {{ transform: translate(-50px,25px) scale(.95); }} }}
.tw {{ fill: {c['fg']}; opacity: .25; animation: tw 6s ease-in-out infinite; }}
@keyframes tw {{ 50% {{ opacity: .8; }} }}
.trail {{ stroke-dasharray: 10 14; animation: dash 3s linear infinite; }}
@keyframes dash {{ to {{ stroke-dashoffset: -48; }} }}
.sweep {{ animation: sweep 6s ease-in-out infinite; }}
@keyframes sweep {{ 0%,100% {{ opacity: .15; }} 50% {{ opacity: .5; }} }}
"""
    return svg_open(W, H, "Ojasva Mishra. Software Engineer at Northrop Grumman. Computer Engineering and Finance at the University of Florida. Robotics and AI.", style) + f'''
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg0']}"/><stop offset="1" stop-color="{c['bg1']}"/></linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c['fg']}"/><stop offset=".55" stop-color="{c['fg']}"/><stop offset="1" stop-color="{c['blue']}"/></linearGradient>
  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c['blue']}"/><stop offset=".5" stop-color="{c['violet']}"/><stop offset="1" stop-color="{c['green']}"/></linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <linearGradient id="fadeR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c['bg0']}" stop-opacity=".95"/><stop offset=".55" stop-color="{c['bg0']}" stop-opacity=".6"/><stop offset="1" stop-color="{c['bg0']}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g filter="url(#blur)" opacity="{c['glow']}">
    <circle class="blob" cx="980" cy="120" r="170" fill="{c['blue']}"/>
    <circle class="blob b2" cx="760" cy="380" r="150" fill="{c['violet']}"/>
    <circle class="blob b3" cx="1140" cy="400" r="120" fill="{c['green']}"/>
  </g>
  <g stroke="{c['grid']}" stroke-width="1" opacity=".7">{grid}</g>
  <g>{stars}</g>
  <rect width="760" height="{H}" fill="url(#fadeR)"/>

  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle class="sweep" cx="{bx}" cy="{by}" r="{l1 + l2}" stroke="{c['muted']}" stroke-width="1.5" stroke-dasharray="3 9"/>
    <path class="trail" d="{trail_d}" stroke="{c['green']}" stroke-width="2.5" opacity=".9"/>
  </g>
  <g>
    <rect x="{bx - 46}" y="{by + 6}" width="92" height="22" rx="6" fill="{c['card2']}" stroke="{c['border']}" stroke-width="2"/>
    <g transform="rotate({-a1:.1f} {bx} {by})">
      <animateTransform attributeName="transform" type="rotate" values="{sh}" dur="8s" repeatCount="indefinite"/>
      <line x1="{bx}" y1="{by}" x2="{bx + l1}" y2="{by}" stroke="{c['fg']}" stroke-width="16" stroke-linecap="round"/>
      <g transform="rotate({-a2:.1f} {bx + l1} {by})">
        <animateTransform attributeName="transform" type="rotate" values="{el}" dur="8s" repeatCount="indefinite"/>
        <line x1="{bx + l1}" y1="{by}" x2="{bx + l1 + l2}" y2="{by}" stroke="{c['blue']}" stroke-width="12" stroke-linecap="round"/>
        <path d="M{bx + l1 + l2 + 4},{by - 14} h14 M{bx + l1 + l2 + 4},{by + 14} h14 M{bx + l1 + l2 + 4},{by - 14} v28" stroke="{c['blue']}" stroke-width="5" fill="none" stroke-linecap="round"/>
        <circle cx="{bx + l1}" cy="{by}" r="11" fill="{c['bg1']}" stroke="{c['fg']}" stroke-width="4"/>
      </g>
      <circle cx="{bx}" cy="{by}" r="14" fill="{c['bg1']}" stroke="{c['fg']}" stroke-width="4"/>
    </g>
  </g>

  <text x="70" y="178" font-family="{SANS}" font-size="92" font-weight="800" letter-spacing="-3" fill="url(#name)">Ojasva Mishra</text>
  <rect x="74" y="206" width="132" height="5" rx="2.5" fill="url(#rule)"/>
  <text x="72" y="262" font-family="{SANS}" font-size="34" font-weight="600" fill="{c['fg']}">Software Engineer at Northrop Grumman</text>
  <text x="72" y="308" font-family="{SANS}" font-size="27" fill="{c['muted']}">Computer Engineering + Finance at UF</text>
  <text x="72" y="368" font-family="{MONO}" font-size="21" fill="{c['muted']}"><tspan fill="{c['blue']}">robotics</tspan>  /  <tspan fill="{c['violet']}">AI systems</tspan>  /  <tspan fill="{c['green']}">quant research</tspan></text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{c['border']}" stroke-width="2"/>
</svg>
'''


# ------------------------------------------------------------------ now
NOW = [
    ("Northrop Grumman", "Software Engineer", "blue"),
    ("Drift", "Founding AI/software engineer", "green"),
    ("CMU Xu Lab", "Robotics research, 3 first-author papers", "violet"),
    ("Twinly", "Co-founder and CEO", "amber"),
]


def now(c):
    W, H = 1200, 360
    tw, th, gap = 584, 164, 32
    tiles = []
    for i, (org, role, col) in enumerate(NOW):
        tx = (i % 2) * (tw + gap)
        ty = (i // 2) * (th + gap)
        hl = i == 0
        tiles.append(f'''
  <g transform="translate({tx},{ty})">
    <rect x="1" y="1" width="{tw - 2}" height="{th - 2}" rx="18" fill="{c['card2'] if not hl else c['card']}" stroke="{c[col] if hl else c['border']}" stroke-width="{3 if hl else 2}"/>
    <rect x="30" y="38" width="8" height="88" rx="4" fill="{c[col]}"/>
    <text x="62" y="80" font-family="{SANS}" font-size="44" font-weight="750" fill="{c['fg']}" letter-spacing="-1">{x(org)}</text>
    <text x="63" y="122" font-family="{SANS}" font-size="27" fill="{c['muted']}">{x(role)}</text>
  </g>''')
    return svg_open(W, H, "Now: " + "; ".join(f"{o}, {r}" for o, r, _ in NOW)) + "".join(tiles) + "\n</svg>\n"


# ------------------------------------------------------------------ numbers
def numbers(c, u):
    W, H = 1200, 230
    stars = {n["name"]: n["stargazerCount"] for n in u["repositories"]["nodes"]}
    contrib = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    items = [
        ("3", "first-author papers", "violet"),
        ("1,000+", "Twinly users", "amber"),
        (f"{stars.get('applytwin', 0)}", "ApplyTwin stars", "green"),
        (f"{contrib:,}", "contributions this year", "blue"),
    ]
    cw = W / 4
    cells = []
    for i, (num, label, col) in enumerate(items):
        cx = cw * i + cw / 2
        cells.append(f'''
  <text x="{cx:.0f}" y="118" text-anchor="middle" font-family="{SANS}" font-size="74" font-weight="800" letter-spacing="-2" fill="{c[col]}">{x(num)}</text>
  <text x="{cx:.0f}" y="170" text-anchor="middle" font-family="{SANS}" font-size="25" fill="{c['muted']}">{x(label)}</text>''')
        if i:
            cells.append(f'<line x1="{cw * i:.0f}" y1="52" x2="{cw * i:.0f}" y2="180" stroke="{c["border"]}" stroke-width="2"/>')
    return svg_open(W, H, "; ".join(f"{n} {l}" for n, l, _ in items)) + f'''
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="{c['card2']}" stroke="{c['border']}" stroke-width="2"/>
{"".join(cells)}
</svg>
'''


# ------------------------------------------------------------------ project cards
def wrap_text(lines, x0, y0, size, lh, fill, weight=400):
    return "".join(f'<text x="{x0}" y="{y0 + i * lh}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" fill="{fill}">{x(l)}</text>'
                   for i, l in enumerate(lines))


def project(c, title, tag, lines, foot, visual, accent, label):
    W, H = 1200, 430
    style = """
.flow { stroke-dasharray: 8 10; animation: flow 1.6s linear infinite; }
@keyframes flow { to { stroke-dashoffset: -36; } }
.pulse { animation: pulse 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.shim { animation: shim 4s ease-in-out infinite; }
@keyframes shim { 0%,100% { opacity: .35; } 50% { opacity: 1; } }
"""
    return svg_open(W, H, label, style) + f'''
<defs>
  <linearGradient id="pbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['card2']}"/><stop offset="1" stop-color="{c['card']}"/></linearGradient>
  <clipPath id="pf"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#pf)">
  <rect width="{W}" height="{H}" fill="url(#pbg)"/>
  <rect x="0" y="0" width="{W}" height="6" fill="{c[accent]}"/>
  <text x="64" y="92" font-family="{MONO}" font-size="22" fill="{c[accent]}">{x(tag)}</text>
  <text x="62" y="160" font-family="{SANS}" font-size="62" font-weight="800" letter-spacing="-2" fill="{c['fg']}">{x(title)}</text>
  {wrap_text(lines, 64, 218, 28, 40, c['fg'])}
  <text x="64" y="{H - 40}" font-family="{MONO}" font-size="21" fill="{c['muted']}">{foot}</text>
  <g transform="translate(760,64)">{visual}</g>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{c['border']}" stroke-width="2"/>
</svg>
'''


def vis_applytwin(c):
    # scan -> tailor -> apply, a packet moving along the pipe
    nodes = [(60, 60, "scan", "blue"), (200, 150, "tailor", "violet"), (340, 240, "apply", "green")]
    d = "M60,60 C140,60 120,150 200,150 S260,240 340,240"
    out = [f'<path d="{d}" fill="none" stroke="{c["border"]}" stroke-width="6" stroke-linecap="round"/>',
           f'<path class="flow" d="{d}" fill="none" stroke="{c["green"]}" stroke-width="3" stroke-linecap="round"/>']
    for nx, ny, lab, col in nodes:
        out.append(f'<circle cx="{nx}" cy="{ny}" r="30" fill="{c["card"]}" stroke="{c[col]}" stroke-width="4"/>'
                   f'<circle class="pulse" cx="{nx}" cy="{ny}" r="10" fill="{c[col]}"/>'
                   f'<text x="{nx + (44 if lab != "apply" else -44)}" y="{ny + 8}" text-anchor="{"start" if lab != "apply" else "end"}" font-family="{MONO}" font-size="24" fill="{c["fg"]}">{lab}</text>')
    out.append(f'<circle r="8" fill="{c["fg"]}"><animateMotion dur="3.2s" repeatCount="indefinite" path="{d}"/></circle>')
    return "".join(out)


def vis_courtside(c):
    # ball arc with the call made before the bounce
    d = "M20,40 Q150,-30 260,200 Q320,90 400,120"
    table = f'<line x1="0" y1="206" x2="400" y2="206" stroke="{c["muted"]}" stroke-width="5" stroke-linecap="round"/>' \
            f'<line x1="200" y1="206" x2="200" y2="170" stroke="{c["muted"]}" stroke-width="3"/>'
    call_x = 218
    return (table +
            f'<path d="{d}" fill="none" stroke="{c["border"]}" stroke-width="3" stroke-dasharray="4 8"/>'
            f'<line x1="{call_x}" y1="40" x2="{call_x}" y2="206" stroke="{c["amber"]}" stroke-width="3" stroke-dasharray="6 6"/>'
            f'<text x="{call_x - 12}" y="30" text-anchor="end" font-family="{MONO}" font-size="24" fill="{c["amber"]}">call</text>'
            f'<text x="{call_x + 12}" y="30" font-family="{MONO}" font-size="24" fill="{c["fg"]}">-162 ms</text>'
            f'<circle cx="260" cy="206" r="7" fill="none" stroke="{c["green"]}" stroke-width="3"/>'
            f'<text x="260" y="246" text-anchor="middle" font-family="{MONO}" font-size="20" fill="{c["muted"]}">bounce</text>'
            f'<circle r="11" fill="{c["amber"]}"><animateMotion dur="2.4s" repeatCount="indefinite" path="{d}"/></circle>'
            f'<text x="0" y="296" font-family="{MONO}" font-size="20" fill="{c["muted"]}">119.9 fps, none wrong</text>')


def vis_dejaview(c):
    # isometric room drawn as a gaussian-splat point cloud
    rnd = random.Random(7)
    ox, oy, s = 200, 150, 125
    iso = lambda X, Y, Z: (ox + (X - Y) * s * 0.866, oy + (X + Y) * s * 0.5 - Z * s)
    pts = [("floor", rnd.random(), rnd.random(), 0) for _ in range(260)]
    pts += [("wallL", 0, rnd.random(), rnd.random() * 1.05) for _ in range(150)]
    pts += [("wallR", rnd.random(), 0, rnd.random() * 1.05) for _ in range(150)]
    # a box on the floor so it reads as a room with something in it
    for _ in range(70):
        f = rnd.choice(["t", "l", "r"])
        a, b = rnd.random(), rnd.random()
        X, Y, Z = {"t": (.45 + a * .3, .45 + b * .3, .3), "l": (.45, .45 + a * .3, b * .3), "r": (.45 + a * .3, .45, b * .3)}[f]
        pts.append(("box", X + .3, Y + .3, Z) if False else ("box", X, Y, Z))
    cols = {"floor": c["violet"], "wallL": c["blue"], "wallR": c["pink"], "box": c["amber"]}
    out = []
    corners = [iso(0, 0, 1.05), iso(0, 0, 0), iso(1, 0, 0), iso(1, 1, 0), iso(0, 1, 0), iso(0, 0, 0)]
    out.append(f'<path d="M{iso(0,1,1.05)[0]:.0f},{iso(0,1,1.05)[1]:.0f} L{iso(0,0,1.05)[0]:.0f},{iso(0,0,1.05)[1]:.0f} L{iso(1,0,1.05)[0]:.0f},{iso(1,0,1.05)[1]:.0f} M{iso(0,0,1.05)[0]:.0f},{iso(0,0,1.05)[1]:.0f} L{iso(0,0,0)[0]:.0f},{iso(0,0,0)[1]:.0f} M{iso(0,1,0)[0]:.0f},{iso(0,1,0)[1]:.0f} L{iso(0,0,0)[0]:.0f},{iso(0,0,0)[1]:.0f} L{iso(1,0,0)[0]:.0f},{iso(1,0,0)[1]:.0f}" fill="none" stroke="{c["dim"]}" stroke-width="1.5" stroke-dasharray="4 6"/>')
    for i, (f, X, Y, Z) in enumerate(pts):
        px, py = iso(X, Y, Z)
        out.append(f'<circle class="shim" cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(1.4, 3.4):.1f}" fill="{cols[f]}" '
                   f'opacity=".85" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    # camera frustum
    cx, cy = 360, 20
    out.append(f'<path d="M{cx},{cy} L{cx - 70},{cy + 40} M{cx},{cy} L{cx - 50},{cy + 70}" stroke="{c["fg"]}" stroke-width="2" opacity=".6"/>'
               f'<rect x="{cx - 4}" y="{cy - 14}" width="34" height="24" rx="5" fill="{c["fg"]}"/>')
    out.append(f'<text x="0" y="296" font-family="{MONO}" font-size="20" fill="{c["muted"]}">~1M Gaussians, 11 min</text>')
    return "".join(out)


def lang_foot(c, info):
    lang = (info or {}).get("primaryLanguage") or {}
    stars = (info or {}).get("stargazerCount", 0)
    parts = []
    if lang:
        parts.append(f'<tspan fill="{lang.get("color") or c["muted"]}">●</tspan> {x(lang["name"])}')
    parts.append(f"★ {stars}")
    return "    ".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    u = fetch()
    by = {n["name"]: n for n in u["repositories"]["nodes"]}
    for t, c in THEMES.items():
        write(f"hero-{t}.svg", hero(c))
        write(f"now-{t}.svg", now(c))
        write(f"numbers-{t}.svg", numbers(c, u))
        write(f"applytwin-{t}.svg", project(
            c, "ApplyTwin", "flagship / open source",
            ["Free job search on autopilot. Finds", "internships that fit, tailors a resume",
             "per posting, and fills the applications", "on your own Claude Code or Codex plan."],
            lang_foot(c, by.get("applytwin")), vis_applytwin(c), "green",
            "ApplyTwin: free, open-source job search on autopilot. Finds internships, tailors a resume per posting, fills applications on your own Claude Code or Codex plan."))
        write(f"courtside-{t}.svg", project(
            c, "Courtside", "Gator Quant Hacks 2026",
            ["A computer-vision ball tracker that calls", "the point a median 162 ms before the",
             "bounce, and a latency study of 13,084", "Polymarket tennis markets."],
            lang_foot(c, by.get("computervision_quant_strategy")), vis_courtside(c), "amber",
            "Courtside: CV ball tracker that calls the point a median 162 ms before the bounce at 119.9 fps; latency study of 13,084 Polymarket markets."))
        write(f"dejaview-{t}.svg", project(
            c, "Déjà View", "SwampHacks XII / 1st AI/ML, 1st DeepSpace",
            ["Photos or video of any space become a", "3D world you walk into on Meta Quest,",
             "in a browser, or in Roblox."],
            lang_foot(c, by.get("Deja-View")), vis_dejaview(c), "violet",
            "Deja View: photos or video of any space become a walkable 3D world on Meta Quest, the web, or Roblox. SwampHacks XII, 1st in two tracks."))
    print("built", len(os.listdir(OUT)), "files")


if __name__ == "__main__":
    main()
