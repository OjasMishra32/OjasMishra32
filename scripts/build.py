"""Builds the profile SVGs in assets/ (dark + light).

Static text lives here; repo stars, followers, contributions and the
language mix come from the GitHub API, so the cards stay current when the
workflow reruns. Uses only the standard library.
"""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "OjasMishra32"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": dict(bg="#0d1117", card="#0d1117", border="#30363d", fg="#e6edf3", muted="#8b949e",
                 faint="#21262d", accent="#58a6ff", accent2="#3fb950", ghost="#6e7681", key="#79c0ff"),
    "light": dict(bg="#ffffff", card="#f6f8fa", border="#d0d7de", fg="#1f2328", muted="#59636e",
                  faint="#e4e8ec", accent="#0969da", accent2="#1a7f37", ghost="#9198a1", key="#0550ae"),
}

# Repos that are not his code (vendored copies, build output) stay out of the language mix.
LANG_SKIP_REPOS = {"DeepSeek-Free-API", "twinner-web", "twinlypitchdeck", "OjasMishra32"}
LANG_SKIP = {"HTML", "CSS", "SCSS", "Jupyter Notebook", "Shell", "Dockerfile", "Makefile"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        name stargazerCount description url pushedAt
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
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


# ---------------------------------------------------------------- header
TYPED = [
    "founding engineer at Drift, robotics AI workspace",
    "first-author robot control papers, CMU Xu Lab",
    "co-founder and CEO of Twinly",
    "quant research at AlgoGators",
    "open source: ApplyTwin",
]


def step_response(clamp):
    q = v = 0.0
    dt, pts = 0.01, []
    for i in range(1001):
        pts.append((i * dt, q))
        u = 6.0 * (1 - q) - 1.1 * v
        if clamp:
            u = max(-clamp, min(clamp, u))
        v += u * dt
        q += v * dt
    return pts


def header(c):
    W, H = 1200, 320
    X0, X1, Y0, Y1 = 760, 1136, 70, 238
    ym = lambda q: Y1 - q / 1.35 * (Y1 - Y0)
    xm = lambda t: X0 + t / 10 * (X1 - X0)
    path = lambda pts: "M" + " L".join(f"{xm(t):.1f},{ym(q):.1f}" for t, q in pts[::6])

    dots = "".join(f'<circle cx="{gx}" cy="{gy}" r="1.4"/>'
                   for gx in range(X0, X1 + 1, 47) for gy in range(Y0, Y1 + 1, 42))

    # Rotating line: phrases cross-fade and rise in turn. Only opacity and a
    # small translate are animated (linear, strictly increasing keyTimes), so
    # there is never partial text on screen. With animation off, the opacity
    # attributes leave exactly the first phrase visible.
    cw, slot, tx, ty, fs = 12.0, 3.2, 66, 246, 20
    fade = 0.35
    total = slot * len(TYPED)
    lines = []
    for i, s in enumerate(TYPED):
        w = len(s) * cw
        a, b = i * slot, (i + 1) * slot
        pts = [(a, 0.0, 8.0), (a + fade, 1.0, 0.0), (b - fade, 1.0, 0.0), (b, 0.0, -8.0)]
        if a > 0:
            pts.insert(0, (0.0, 0.0, 8.0))
        if b < total:
            pts.append((total, 0.0, 8.0))
        kt = ";".join(f"{t / total:.4f}" for t, _, _ in pts)
        op = ";".join(f"{o:g}" for _, o, _ in pts)
        dy = ";".join(f"0 {d:g}" for _, _, d in pts)
        anim = (f'<animate attributeName="opacity" values="{op}" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{dy}" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>')
        lines.append(f'''
    <g opacity="{1 if i == 0 else 0}">{anim}
      <text x="{tx}" y="{ty}" textLength="{w:.0f}" lengthAdjust="spacingAndGlyphs" font-family="{MONO}" font-size="{fs}" fill="{c['fg']}">{x(s)}</text>
      <rect class="blink" x="{tx + w + 4:.0f}" y="{ty - 18}" width="10" height="23" fill="{c['accent']}"/>
    </g>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Ojasva Mishra. Computer Engineering and Finance at the University of Florida.">
  <style>
    .draw {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 2.6s cubic-bezier(.3,.7,.2,1) .3s forwards; }}
    .ghost {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 2.6s ease-out .1s forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    .blink {{ animation: blink 1.1s steps(1) infinite; }}
    @media (max-width: 700px) {{ .viz {{ display: none; }} .txt {{ transform: translate(-22px,-64px) scale(1.42); }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .draw, .ghost, .blink {{ animation: none; stroke-dashoffset: 0; }} }}
  </style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{c['card']}" stroke="{c['border']}" stroke-width="2"/>
  <g class="txt">
  <g>
    <text x="62" y="120" fill="{c['fg']}" font-family="{SANS}" font-size="64" font-weight="700" letter-spacing="-1.5">Ojasva Mishra</text>
    <text x="65" y="168" fill="{c['muted']}" font-family="{SANS}" font-size="25">Computer Engineering + Finance, University of Florida</text>
    <text x="66" y="206" fill="{c['accent']}" font-family="{MONO}" font-size="17">robotics / AI systems / quant research</text>
    <text x="40" y="246" fill="{c['accent2']}" font-family="{MONO}" font-size="20">&gt;</text>
  </g>
  {"".join(lines)}
  </g>
  <g class="viz">
  <g fill="{c['faint']}">{dots}</g>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <line x1="{X0}" y1="{ym(1):.1f}" x2="{X1}" y2="{ym(1):.1f}" stroke="{c['ghost']}" stroke-width="1.5" stroke-dasharray="5 7"/>
    <path class="ghost" pathLength="1" d="{path(step_response(None))}" stroke="{c['ghost']}" stroke-width="2" opacity=".55"/>
    <path class="draw" pathLength="1" d="{path(step_response(1.6))}" stroke="{c['accent']}" stroke-width="3.5"/>
  </g>
  <g font-family="{MONO}" font-size="14" fill="{c['muted']}">
    <text x="{X0}" y="{Y1 + 36}">joint step response, torque-limited</text>
    <text x="{X1}" y="{ym(1) - 12:.1f}" text-anchor="end">q_ref</text>
  </g>
  </g>
</svg>
'''


# ---------------------------------------------------------------- about card
# Neofetch-style card, after Andrew6rant's profile layout (technique only,
# no code reused). The ASCII art is his portrait.
# a portrait of him in ASCII, from his headshot (background removed); dark mode lights the face, light mode inks it
PORTRAIT = {"dark": ["", "", "             :---==-:   :", "           .-::.:::..:-==-::", "        -::....:::.....--::.::", "       ::..........:-:.......:-:", "       :........+#%%%%+........--", "       .:....:-+*#%@%%*=:......:", "         ..-#+++==#%#+=+**+....", "         -+*#*++**#@#*++*#%=-", "         +##%%%%%#*##%%%@@@##", "         -%#####***####%%%%@#", "           =########%##%%%#=", "            ***##%%%%@%###", "          :#%++++****##*%", "        --:+@%*+=++++*##%#:", "   --====-::*@@%#*****##@@++=-", "++++=-===--::%@@@@@##*%@@%-=+*++=-", "==-----==---:=@@@%##***#@%--=++=++++", "-------------:+@%=--+##+*#-=========", "--===--===-----#@@%+-=*#@*-====++==="], "light": ["", "", "             #***++*#   #", "           %*##%###%%#*++*##", "        *##%%%%###%@@@%**##%##", "       ##%%@%%%%%%%#*#%%%%%%%#*#", "       #%%%@@@@%=:....=%@@%%%@%**", "       %#%%%%#*=-:....-+#%@@%@%#", "         %@*:===++:.:=+=--=%@%%", "         *=-:-==--:.:-==-:.+*", "         =::.....:-::......::", "         *.:::::---::::.....:", "           +::::::::.::...:+", "            ---::......:::", "          #:.====----::-.", "        **#=..-=+====-::.:#", "   **++++*##-...:-----::..==+*", "====+*+++**##......::-....*+=-==+*", "++*****++***#+....::---:..**+==+====", "*************#=..+**=::=-:*+++++++++", "**+++**+++*****:...=*+-:.-*++++==+++"]}

NEO = {
    "dark": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f", art="#c9d1d9"),
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", cc="#c2cfde", art="#24292f"),
}

ROWS = [
    ("Education", "UF, B.S. CompE + Finance, 2029"),
    ("Building", "Drift (Antler), Twinly (Z Fellows)"),
    ("Research", "CMU Xu Lab, 3 first-author papers"),
    ("Venues", "IEEE T-RO, ICRA 2027, IROS 2026"),
    ("Quant", "AlgoGators quant research"),
    None,
    ("Languages.Programming", "Python, C++, Rust, Swift, TS"),
    ("Languages.Real", "English, Hindi, German"),
    ("Robotics", "ROS2, MuJoCo, Isaac Sim, PX4"),
    ("AI", "PyTorch, OpenCV, VLMs, LLM agents"),
]
CONTACT = [("Website", "ojasvamishra.me"), ("Email", "ojasvamishra32@gmail.com"), ("LinkedIn", "in/ojasvamishra"), ("GitHub", "OjasMishra32")]
WIDTH = 58  # characters per right-hand line


def about(theme, u):
    c = NEO[theme]
    W = 985
    repos = u["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    contrib = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    follow = u["followers"]["totalCount"]

    def kv(key, value):
        parts = key.split(".")
        keys = '<tspan class="cc">.</tspan>'.join(f'<tspan class="key">{x(k)}</tspan>' for k in parts)
        dots = "." * max(1, WIDTH - len(key) - len(value) - 5)
        return f'<tspan class="cc">. </tspan>{keys}:<tspan class="cc"> {dots} </tspan><tspan class="value">{x(value)}</tspan>'

    def rule(title):
        return f'- {x(title)} <tspan class="cc">{"-" * (WIDTH - len(title) - 3)}</tspan>'

    lines = [f'ojasva@mishra <tspan class="cc">{"-" * (WIDTH - 14)}</tspan>']
    for r in ROWS:
        lines.append('<tspan class="cc">. </tspan>' if r is None else kv(*r))
    lines.append("")
    lines.append(rule("Contact"))
    for r in CONTACT:
        lines.append(kv(*r))
    lines.append("")
    lines.append(rule("GitHub Stats"))
    def pair(k1, v1, k2, v2):
        left = f"{k1}: {v1}"
        return (f'<tspan class="cc">. </tspan><tspan class="key">{k1}</tspan>:<tspan class="cc"> {"." * (24 - len(left))} </tspan><tspan class="value">{v1}</tspan>'
                f' | <tspan class="key">{k2}</tspan>:<tspan class="cc"> {"." * max(1, WIDTH - 33 - len(k2) - len(str(v2)))} </tspan><tspan class="value">{v2}</tspan>')
    lines.append(pair("Repos", repos["totalCount"], "Stars", stars))
    lines.append(pair("Followers", follow, "Contributions", f"{contrib:,}"))

    H = 34 + 20 * len(lines) + 10
    art_lines = PORTRAIT[theme]
    top = 34 + (len(lines) - len(art_lines)) * 10
    art = "".join(f'<tspan x="20" y="{top + i * 20}">{x(l)}</tspan>' for i, l in enumerate(art_lines))
    body = "".join(f'<tspan x="400" y="{34 + i * 20}">{l}</tspan>' for i, l in enumerate(lines))
    # phone layout: the README column is ~330px there, so fewer, larger lines
    short = [("ojasva@mishra", None), ("UF", "CompE + Finance, 2029"), ("Building", "Drift, Twinly"),
             ("Research", "CMU, 3 papers"), ("Quant", "AlgoGators"), ("Code", "Python, C++, Rust"),
             ("Stars", f"{stars}, {contrib:,} contribs")]
    nfs, nlh = 36, (H - 40) / len(short)
    narrow = "".join(
        (f'<text x="44" y="{40 + nlh * (i + .6):.0f}" fill="{c["text"]}" font-weight="700">{x(k)}</text>' if v is None else
         f'<text x="44" y="{40 + nlh * (i + .6):.0f}"><tspan class="key">{x(k)}</tspan><tspan class="cc">: </tspan><tspan class="value">{x(v)}</tspan></text>')
        for i, (k, v) in enumerate(short))
    ptop = (H - 15 * len(art_lines)) / 2 + 12
    narrow += f'<text fill="{c["art"]}" font-size="10.5" xml:space="preserve">' + "".join(
        f'<tspan x="738" y="{ptop + i * 15:.0f}">{x(l)}</tspan>' for i, l in enumerate(art_lines)) + '</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="16" role="img" aria-label="ojasva@mishra. UF Computer Engineering and Finance, 2029. Building Drift and Twinly. CMU Xu Lab, 3 first-author papers. AlgoGators quant research. Live GitHub stats.">
<style>
.key {{ fill: {c['key']}; }} .value {{ fill: {c['value']}; }} .cc {{ fill: {c['cc']}; }}
text, tspan {{ white-space: pre; }}
.n {{ display: none; }}
@media (max-width: 700px) {{ .w {{ display: none; }} .n {{ display: inline; }} }}
</style>
<rect width="{W}" height="{H}" rx="15" fill="{c['bg']}"/>
<g class="w"><text fill="{c['art']}" xml:space="preserve">{art}</text>
<text fill="{c['text']}" xml:space="preserve">{body}</text></g>
<g class="n" font-size="{nfs}">{narrow}</g>
</svg>
'''


# ---------------------------------------------------------------- project cards
PROJECTS = [
    dict(repo="applytwin", short="Job search on autopilot, open source", title="ApplyTwin", wide=True,
         lines=["Free, open-source job search on autopilot. Finds internships",
                "that fit, tailors a resume to each posting, and fills the",
                "applications, all on your own Claude Code or Codex plan."],
         tag="flagship / open source"),
    dict(repo="volition", short="EEG-driven exoskeleton", title="Volition",
         lines=["Concept exoskeleton for paraplegia, driven by", "EEG motor imagery. CadQuery CAD, 1 kHz sim with",
                "torque saturation and anti-windup, BCI decoder."],
         tag="robotics / BCI"),
    dict(repo="computervision_quant_strategy", short="Calls points 162 ms early", title="Courtside",
         lines=["CV ball tracker calls the point a median 162 ms", "before the bounce at 119.9 fps; latency study",
                "of 13,084 Polymarket tennis markets."],
         tag="Gator Quant Hacks 2026"),
    dict(repo="Deja-View", short="Photos into 3D worlds", title="Déjà View",
         lines=["Photos or video of any space into a walkable", "3D world on Quest, web, or Roblox. ~1M-Gaussian",
                "splat trained on HiPerGator in 11 min."],
         tag="SwampHacks XII, 1st in 2 tracks"),
    dict(repo="fuse", short="Two screens, one AI result", title="FUSE",
         lines=["Native iOS app: fold the iPhone Duo to fuse", "both screens into one AI result.", ""],
         tag="Bitrig Hacks, Y Combinator"),
    dict(repo="eyesight", short="LiDAR obstacle detection", title="Eyesight",
         lines=["LiDAR plus on-device CoreML obstacle", "detection on iPhone.", ""],
         tag="iOS / CoreML"),
    dict(repo="Preventa", short="App Store, rated 5.0", title="PreventaAI",
         lines=["iOS app on the App Store, rated 5.0.", "SwiftUI and Firebase.", ""],
         tag="App Store"),
    dict(repo="twinly-api-examples", short="Twinly API starters", title="Twinly API examples",
         lines=["Starter projects for the Twinly API: iMessage", "bots, calls in your voice, voice notes, tasks.", ""],
         tag="Twinly"),
]

STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"
REPO_ICON = "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"


def card(c, p, info):
    wide = p.get("wide")
    W, H = (1200, 220) if wide else (590, 200)
    fs = 21 if wide else 17
    lh = 30 if wide else 25
    lang = info.get("primaryLanguage") or {}
    stars = info.get("stargazerCount", 0)
    body = "".join(f'<text x="30" y="{(96 if wide else 88) + i * lh}">{x(l)}</text>' for i, l in enumerate(p["lines"]) if l)
    foot_y = H - 26
    lang_svg = ""
    fx = 30
    if lang:
        lang_svg = f'<circle cx="{fx + 7}" cy="{foot_y - 5}" r="7" fill="{lang.get("color") or c["ghost"]}"/><text x="{fx + 22}" y="{foot_y}">{x(lang["name"])}</text>'
        fx += 40 + len(lang["name"]) * 9
    star_svg = f'<g transform="translate({fx},{foot_y - 14}) scale(1.05)" fill="{c["muted"]}"><path d="{STAR}"/></g><text x="{fx + 24}" y="{foot_y}">{stars}</text>'
    flow = ""
    if wide:
        steps = [("scan", "roles that fit you"), ("tailor", "a resume per posting"), ("apply", "fill, submit, log")]
        fy = 92
        for i, (k, v) in enumerate(steps):
            yy = fy + i * 34
            flow += (f'<circle cx="822" cy="{yy - 6}" r="5" fill="{c["accent2"]}"/>'
                     + (f'<line x1="822" y1="{yy}" x2="822" y2="{yy + 22}" stroke="{c["border"]}" stroke-width="2"/>' if i < 2 else "")
                     + f'<text x="840" y="{yy}" font-family="{MONO}" font-size="17"><tspan fill="{c["key"]}">{k}</tspan><tspan fill="{c["muted"]}">  {x(v)}</tspan></text>')
    if wide:
        narrow = (f'<text x="44" y="78" font-family="{SANS}" font-size="56" font-weight="700" fill="{c["accent"]}">{x(p["title"])}</text>'
                  f'<text x="44" y="138" font-family="{SANS}" font-size="38" fill="{c["fg"]}">{x(p["short"])}</text>'
                  f'<text x="44" y="190" font-family="{SANS}" font-size="32" fill="{c["muted"]}">{x(p["tag"])}  ·  ★ {stars}</text>')
    else:
        narrow = (f'<text x="36" y="86" font-family="{SANS}" font-size="62" font-weight="700" fill="{c["accent"]}">{x(p["title"])}</text>'
                  f'<text x="36" y="152" font-family="{SANS}" font-size="40" fill="{c["fg"]}">{x(p["short"])}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{x(p['title'])}: {x(' '.join(p['lines']))}">
  <style>.n {{ display: none; }} @media (max-width: {700 if wide else 300}px) {{ .w {{ display: none; }} .n {{ display: inline; }} }}</style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{c['card']}" stroke="{c['border']}" stroke-width="2"/>
  <g class="n">{narrow}</g>
  <g class="w">
  <g transform="translate(30,{24 if wide else 22}) scale({1.5 if wide else 1.3})" fill="{c['muted']}"><path d="{REPO_ICON}"/></g>
  <text x="{70 if wide else 62}" y="{48 if wide else 42}" font-family="{SANS}" font-size="{30 if wide else 24}" font-weight="700" fill="{c['accent']}">{x(p['title'])}</text>
  <text x="{W - 30}" y="{48 if wide else 42}" text-anchor="end" font-family="{MONO}" font-size="{16 if wide else 14}" fill="{c['accent2']}">{x(p['tag'])}</text>
  <g font-family="{SANS}" font-size="{fs}" fill="{c['fg']}">{body}</g>
  <g font-family="{SANS}" font-size="{17 if wide else 15}" fill="{c['muted']}">{lang_svg}{star_svg}</g>
  {flow}
  </g>
</svg>
'''


SKIP_LATEST = {"OjasMishra32", "OjasMishra32.github.io", "twinner-web", "twinly-releases", "twinly-releases-windows", "twinlypitchdeck"}


def ago(iso):
    import datetime
    d = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = d.days
    return "today" if days < 1 else "yesterday" if days < 2 else f"{days} days ago" if days < 30 else f"{days // 30} months ago"


def latest(u, n=5):
    repos = sorted((r for r in u["repositories"]["nodes"] if r["name"] not in SKIP_LATEST), key=lambda r: r["pushedAt"], reverse=True)[:n]
    rows = []
    for r in repos:
        desc = (r["description"] or "").replace("\u2014", ",").replace("\u2013", "-").split(" Docs:")[0].strip()
        if len(desc) > 72:
            desc = desc[:72].rsplit(" ", 1)[0].rstrip(",.:;") + "..."
        lang = (r["primaryLanguage"] or {}).get("name")
        lang_s = f" · {lang}" if lang else ""
        rows.append(f"- [**{r['name']}**]({r['url']}){lang_s} · <sub>pushed {ago(r['pushedAt'])}</sub>" + (f"<br>{desc}" if desc else ""))
    return "\n".join(rows)


def update_readme(u):
    path = os.path.join(ROOT, "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    a, b = "<!-- LATEST:START -->", "<!-- LATEST:END -->"
    if a in text and b in text:
        i, j = text.index(a) + len(a), text.index(b)
        text = text[:i] + "\n" + latest(u) + "\n" + text[j:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def main():
    os.makedirs(OUT, exist_ok=True)
    u = fetch()
    by_name = {n["name"]: n for n in u["repositories"]["nodes"]}
    for theme, c in THEMES.items():
        write(f"header-{theme}.svg", header(c))
        write(f"about-{theme}.svg", about(theme, u))
        for p in PROJECTS:
            write(f"card-{p['repo'].lower()}-{theme}.svg", card(c, p, by_name.get(p["repo"], {})))
    update_readme(u)
    print("built", len(os.listdir(OUT)), "files")


if __name__ == "__main__":
    main()
