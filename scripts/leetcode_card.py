import math, random, datetime, json, sys

BADGE_COLORS = {50: ("#9aa4b2", "#5b6472"), 100: ("#5aa9ff", "#2a5bd7"), 200: ("#b98cff", "#6d3fd8"),
                365: ("#ffd25a", "#c98a0b"), 500: ("#5fe08f", "#169a4c"), 1000: ("#ff7a7c", "#c0262b")}

def badge_meta(name):
    import re
    m = re.search(r"(\d+)\s*Days", name, re.I)
    if m:
        n = int(m.group(1)); col = BADGE_COLORS.get(n, ("#ffc552", "#d97706"))
        return str(n), "DAYS", f"{n} Days", col
    m = re.search(r"(20\d\d)", name)
    if "annual" in name.lower() and m:
        return m.group(1), "ANNUAL", f"Annual {m.group(1)}", ("#ffb347", "#e0620c")
    short = "".join(w[0] for w in name.split()[:3]).upper()
    return short, "", name[:16], ("#ffc552", "#d97706")

def badge_svg(b, x, y, font):
    big, small, label, (c1, c2) = badge_meta(b["name"])
    gid = f"bg{abs(hash(b['name'])) % 10**6}"
    cx, cy, r = x + 24, y + 22, 23
    pts = " ".join(f"{cx + r*math.cos(math.radians(60*k-90)):.1f},{cy + r*math.sin(math.radians(60*k-90)):.1f}" for k in range(6))
    pts2 = " ".join(f"{cx + (r-5)*math.cos(math.radians(60*k-90)):.1f},{cy + (r-5)*math.sin(math.radians(60*k-90)):.1f}" for k in range(6))
    fs = 13 if len(big) <= 3 else 10.5
    o = [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>',
         f'<polygon points="{pts}" fill="{c2}" fill-opacity=".18" stroke="url(#{gid})" stroke-width="2"/>',
         f'<polygon points="{pts2}" fill="url(#{gid})" fill-opacity=".9"/>',
         f'<text x="{cx}" y="{cy + (2 if small else 5)}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="#0d1117">{big}</text>']
    if small:
        o.append(f'<text x="{cx}" y="{cy + 11}" text-anchor="middle" font-size="5.5" font-weight="800" letter-spacing=".6" fill="#0d1117" fill-opacity=".8">{small}</text>')
    o.append(f'<text x="{x + 56}" y="{y + 19}" font-size="13" font-weight="700" fill="#e6edf3">{label}</text>')
    if b.get("date"):
        o.append(f'<text x="{x + 56}" y="{y + 35}" font-size="10.5" fill="#8b949e">{b["date"]}</text>')
    return "".join(o)

def max_streak(cal):
    best = cur = 0; prev = None
    for k in sorted(k for k, v in cal.items() if v):
        dd = datetime.date.fromisoformat(k)
        cur = cur + 1 if prev and (dd - prev).days == 1 else 1
        best = max(best, cur); prev = dd
    return best

def card(d, out):
    badges = d.get("badges", [])[:4]
    W, H = 840, 428 + (76 if badges else 0)
    E, M, Hd = d["easy"], d["medium"], d["hard"]
    TE, TM, TH = d["tot_easy"], d["tot_medium"], d["tot_hard"]
    solved, total = E+M+Hd, TE+TM+TH
    C = dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3", dim="#8b949e",
             easy="#2ecc71", med="#ffa116", hard="#ff4d4f", track="#21262d")
    font = "'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    a(f'''<style>
text{{font-family:{font};font-feature-settings:"tnum";}}
.fade{{opacity:0;animation:f .6s ease forwards}}
@keyframes f{{to{{opacity:1}}}}
.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:g 1.2s cubic-bezier(.2,.8,.2,1) .3s forwards}}
@keyframes g{{to{{transform:scaleX(1)}}}}
.arc{{animation:r 1.4s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes r{{from{{stroke-dashoffset:var(--o)}}}}
.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}
</style>''')
    a(f'''<defs>
<linearGradient id="bgG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#11161f"/><stop offset="1" stop-color="#0a0d13"/></linearGradient>
<radialGradient id="glow" cx="0.12" cy="0.1" r="0.6"><stop offset="0" stop-color="#ffa116" stop-opacity=".13"/><stop offset="1" stop-color="#ffa116" stop-opacity="0"/></radialGradient>
<linearGradient id="gE" x1="0" x2="1"><stop offset="0" stop-color="#1fa463"/><stop offset="1" stop-color="#3ee088"/></linearGradient>
<linearGradient id="gM" x1="0" x2="1"><stop offset="0" stop-color="#e8890c"/><stop offset="1" stop-color="#ffc04d"/></linearGradient>
<linearGradient id="gH" x1="0" x2="1"><stop offset="0" stop-color="#e5383b"/><stop offset="1" stop-color="#ff7a7c"/></linearGradient>
<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>''')
    a(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="url(#bgG)" stroke="{C["border"]}"/>')
    a(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="url(#glow)"/>')
    # leetcode-ish logo
    a(f'''<g transform="translate(28,26) scale(1.5)" class="fade">
<path d="M16.1 22.6a2 2 0 0 1-2.8.1l-6.2-6a3.3 3.3 0 0 1 0-4.7L13 6a2 2 0 0 1 2.8 0" fill="none" stroke="#ffa116" stroke-width="2.4" stroke-linecap="round"/>
<path d="M10.3 14.4h9" stroke="#b3b3b3" stroke-width="2.4" stroke-linecap="round"/>
<path d="M16.1 22.6l2.2-2.2" stroke="#e6edf3" stroke-width="2.4" stroke-linecap="round"/></g>''')
    a(f'<text x="80" y="47" font-size="22" font-weight="700" letter-spacing="-.3" fill="{C["text"]}" class="fade">{d["user"]}</text>')
    a(f'<text x="80" y="66" font-size="12.5" fill="{C["dim"]}" class="fade">LeetCode  ·  Problem Solving Stats</text>')
    rank = f'{d["rank"]:,}'
    rw = 150 + 9.5*len(rank)
    a(f'<g class="fade"><rect x="{W-24-rw}" y="28" width="{rw}" height="32" rx="16" fill="#ffa116" fill-opacity=".08" stroke="#ffa116" stroke-opacity=".35"/>')
    a(f'<text x="{W-24-rw/2}" y="49" text-anchor="middle" font-size="12" font-weight="600" letter-spacing=".8" fill="{C["dim"]}">GLOBAL RANK  <tspan font-size="14" letter-spacing="0" fill="{C["med"]}" font-weight="700">#{rank}</tspan></text></g>')
    a(f'<line x1="24" x2="{W-24}" y1="84" y2="84" stroke="{C["border"]}" stroke-opacity=".7"/>')
    # donut
    cx, cy, R, sw = 120, 178, 64, 11
    circ = 2*math.pi*R
    a(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{C["track"]}" stroke-width="{sw}"/>')
    frac = solved/total
    ringfrac = 1
    gap = 6
    start = 0
    for val, col in [(E, "url(#gE)"), (M, "url(#gM)"), (Hd, "url(#gH)")]:
        L = circ*ringfrac*val/max(solved,1)
        seg = max(L-gap, 1)
        a(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
          f'stroke-dasharray="{seg:.2f} {circ:.2f}" stroke-dashoffset="{-start:.2f}" style="--o:{-start+seg:.2f}" class="arc" transform="rotate(-90 {cx} {cy})"/>')
        start += L
    a(f'<circle cx="{cx}" cy="{cy}" r="{R-16}" fill="#ffa116" fill-opacity=".05" filter="url(#sh)"/>')
    a(f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-size="38" letter-spacing="-1" font-weight="700" fill="{C["text"]}">{solved}</text>')
    a(f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-size="10.5" font-weight="600" letter-spacing="1.5" fill="{C["dim"]}">SOLVED</text>')
    a(f'<text x="{cx}" y="{cy+R+28}" text-anchor="middle" font-size="11" fill="{C["dim"]}"><tspan fill="{C["med"]}" font-weight="700">{frac*100:.1f}%</tspan> of {total:,}</text>')
    # bars
    bx, bw = 238, 370
    for i, (lab, v, t, col, gr) in enumerate([("Easy", E, TE, C["easy"], "url(#gE)"), ("Medium", M, TM, C["med"], "url(#gM)"), ("Hard", Hd, TH, C["hard"], "url(#gH)")]):
        y = 120 + i*50
        a(f'<g class="fade" style="animation-delay:{.1*i:.1f}s">')
        a(f'<circle cx="{bx+4}" cy="{y-5}" r="4" fill="{col}"/>')
        a(f'<text x="{bx+16}" y="{y}" font-size="14" font-weight="600" fill="{C["text"]}">{lab}<tspan dx="8" font-size="11.5" font-weight="500" fill="{C["dim"]}">{v/t*100:.1f}%</tspan></text>')
        a(f'<text x="{bx+bw}" y="{y}" text-anchor="end" font-size="13" fill="{C["dim"]}"><tspan fill="{C["text"]}" font-weight="700">{v}</tspan> / {t}</text>')
        a(f'<rect x="{bx}" y="{y+10}" width="{bw}" height="8" rx="4" fill="{C["track"]}"/>')
        a(f'<rect x="{bx}" y="{y+10}" width="{max(bw*v/t,8):.1f}" height="8" rx="4" fill="{gr}" class="bar" style="animation-delay:{.3+.15*i:.2f}s"/>')
        a('</g>')
    # side stat tiles
    tx, tw = 636, 180
    tiles = [("Max streak", f'{d.get("max_streak", 0)} days', C["med"]),
             ("Hard share", f"{Hd/max(solved,1)*100:.0f}%", C["hard"]),
             ("Active days", f'{d["active_days"]}', C["easy"])]
    for i, (lab, val, col) in enumerate(tiles):
        y = 102 + i*56
        a(f'<g class="fade" style="animation-delay:{.2+.1*i:.1f}s"><rect x="{tx}" y="{y}" width="{tw}" height="46" rx="8" fill="{C["panel"]}" stroke="{C["border"]}"/>')
        a(f'<rect x="{tx}" y="{y+10}" width="3" height="26" rx="1.5" fill="{col}"/>')
        a(f'<text x="{tx+16}" y="{y+19}" font-size="10" font-weight="600" letter-spacing="1" fill="{C["dim"]}">{lab.upper()}</text>')
        a(f'<text x="{tx+16}" y="{y+37}" font-size="18" font-weight="700" fill="{C["text"]}">{val}</text></g>')
    # heatmap
    hy = 296
    a(f'<line x1="24" x2="{W-24}" y1="{hy-16}" y2="{hy-16}" stroke="{C["border"]}" stroke-opacity=".7"/>')
    cal = d["calendar"]  # dict date->count
    end = datetime.date.fromisoformat(d["end"])
    startd = end - datetime.timedelta(days=7*52 + end.weekday() + 1 - 7)  # align to Sunday
    while startd.weekday() != 6: startd -= datetime.timedelta(days=1)
    cell, g = 10, 3
    weeks = ((end - startd).days)//7 + 1
    gx = W - 24 - weeks*(cell+g) + g
    a(f'<text x="24" y="{hy+4}" font-size="10" font-weight="600" letter-spacing="1" fill="{C["dim"]}">ACTIVITY</text>')
    a(f'<text x="24" y="{hy+20}" font-size="10" fill="{C["dim"]}">last 52 weeks</text>')
    a(f'<text x="24" y="{hy+62}" font-size="22" font-weight="700" fill="{C["text"]}">{sum(cal.values())}</text>')
    a(f'<text x="24" y="{hy+78}" font-size="10.5" fill="{C["dim"]}">submissions</text>')
    pal = ["#1c2129", "#b4570a", "#dc7410", "#f7951a", "#ffc552"]
    mx = max(list(cal.values()) or [1])
    last_m = None
    for w in range(weeks):
        for dd in range(7):
            day = startd + datetime.timedelta(days=w*7+dd)
            if day > end: continue
            if dd == 0 and day.month != last_m and 1 < w < weeks-2:
                a(f'<text x="{gx+w*(cell+g)}" y="{hy-1}" font-size="9" fill="{C["dim"]}">{day.strftime("%b")}</text>')
                last_m = day.month
            v = cal.get(day.isoformat(), 0)
            lvl = 0 if v == 0 else (1 if v == 1 else 2 if v == 2 else 3 if v <= 4 else 4)
            a(f'<rect x="{gx+w*(cell+g)}" y="{hy+6+dd*(cell+g)}" width="{cell}" height="{cell}" rx="2.5" fill="{pal[lvl]}" class="fade" style="animation-delay:{w*0.012:.3f}s"/>')
    # legend
    lx = W - 24 - 5*(cell+g) - 60
    ly = hy + 6 + 7*(cell+g) + 4
    a(f'<text x="{lx-6}" y="{ly+9}" text-anchor="end" font-size="9" fill="{C["dim"]}">less</text>')
    for i, c in enumerate(pal):
        a(f'<rect x="{lx+i*(cell+g)}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" fill="{c}"/>')
    a(f'<text x="{lx+5*(cell+g)+4}" y="{ly+9}" font-size="9" fill="{C["dim"]}">more</text>')
    if badges:
        by = ly + 30
        a(f'<line x1="24" x2="{W-24}" y1="{by-12}" y2="{by-12}" stroke="{C["border"]}" stroke-opacity=".7"/>')
        a(f'<text x="24" y="{by+12}" font-size="10" font-weight="600" letter-spacing="1" fill="{C["dim"]}">BADGES</text>')
        a(f'<text x="24" y="{by+28}" font-size="10.5" fill="{C["dim"]}">consistency awards</text>')
        bw2 = (W - 24 - 150) / 4
        for i, b in enumerate(badges):
            bx2 = 150 + i*bw2
            a(f'<g class="fade" style="animation-delay:{.5+.12*i:.2f}s">' + badge_svg(b, bx2, by, font) + '</g>')
    a('</svg>')
    open(out, "w").write("\n".join(s))
    return H + 0

QUERY = """query($u:String!){
  allQuestionsCount{difficulty count}
  matchedUser(username:$u){
    profile{ranking}
    submitStatsGlobal{acSubmissionNum{difficulty count}}
    userCalendar{submissionCalendar}
    badges{displayName creationDate}
  }
}"""

def fetch(user):
    import urllib.request, time
    body = json.dumps({"query": QUERY, "variables": {"u": user}}).encode()
    req = urllib.request.Request("https://leetcode.com/graphql", data=body, headers={
        "Content-Type": "application/json", "Referer": f"https://leetcode.com/u/{user}/",
        "User-Agent": "Mozilla/5.0 (leetcode-card-action)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)["data"]
            break
        except Exception as e:
            print("fetch failed:", e)
            if attempt == 3: raise
            time.sleep(5 * (attempt + 1))
    u = data["matchedUser"]
    if not u: raise SystemExit(f"user {user} not found")
    tot = {x["difficulty"]: x["count"] for x in data["allQuestionsCount"]}
    ac = {x["difficulty"]: x["count"] for x in u["submitStatsGlobal"]["acSubmissionNum"]}
    end = datetime.datetime.now(datetime.timezone.utc).date()
    start = end - datetime.timedelta(days=371)
    cal = {}
    for ts, n in json.loads(u["userCalendar"]["submissionCalendar"] or "{}").items():
        day = datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).date()
        if start <= day <= end:
            cal[day.isoformat()] = cal.get(day.isoformat(), 0) + int(n)
    return dict(user=user, rank=u["profile"]["ranking"] or 0,
                easy=ac.get("Easy", 0), medium=ac.get("Medium", 0), hard=ac.get("Hard", 0),
                tot_easy=tot["Easy"], tot_medium=tot["Medium"], tot_hard=tot["Hard"],
                active_days=sum(1 for v in cal.values() if v), calendar=cal, end=end.isoformat(),
                max_streak=max_streak(cal), badges=pick_badges(u.get("badges") or []))

def pick_badges(raw):
    bs = [{"name": b.get("displayName") or "", "date": b.get("creationDate") or ""} for b in raw]
    def prio(b):
        n = b["name"].lower()
        return (0 if "days" in n or "annual" in n else 1, b["date"])
    bs.sort(key=lambda b: b["date"], reverse=True)
    bs.sort(key=lambda b: 0 if ("days" in b["name"].lower() or "annual" in b["name"].lower()) else 1)
    return bs[:4]

if __name__ == "__main__":
    import os
    user = sys.argv[1] if len(sys.argv) > 1 else "Animesh_Sen"
    out = sys.argv[2] if len(sys.argv) > 2 else "assets/leetcode-card.svg"
    if user == "--demo":
        random.seed(7); end = datetime.date(2026, 11, 21); cal = {}
        for i in range(364):
            if random.random() < .6: cal[(end - datetime.timedelta(days=i)).isoformat()] = random.randint(1, 6)
        d = dict(user="Animesh_Sen", rank=145878, easy=163, medium=320, hard=121, tot_easy=977, tot_medium=2150,
                 tot_hard=992, active_days=len(cal), calendar=cal, end=end.isoformat())
    else:
        d = fetch(user)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    card(d, out)
    print(f"wrote {out}: {d['easy']+d['medium']+d['hard']} solved, rank {d['rank']}")
