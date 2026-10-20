"""Build index.html from content.txt.  Usage: python3 build.py"""
import html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def inline(s, where="main"):
    s = html.escape(s, quote=False)
    s = re.sub(r"==(.+?)==", (r'<span class="hl">\1</span>' if where == "main" else r'<span class="em">\1</span>'), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\{(.+?)\}", r'<mark class="todo">\1</mark>', s)
    return s


def anchors(s, start):
    n = [start]
    def f(m):
        n[0] += 1; return f'<span class="an" data-n="{n[0]-1}">{m.group(1)}</span>'
    return re.sub(r"\[\[(.+?)\]\]", f, s), n[0]


def parse(path):
    meta, links, entries, mode = {}, [], [], None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("== "):
            entries.append({"date": line[3:].strip(), "main": [], "note": []}); mode = "entry"; continue
        if mode == "entry":
            if line.startswith(">>"):
                entries[-1]["note"][-1] += "\n" + line[2:].strip()
            else:
                (entries[-1]["note"] if line.startswith(">") else entries[-1]["main"]).append(line.lstrip("> ").strip())
            continue
        if line.strip() == "links:":
            mode = "links"; continue
        if mode == "links" and "|" in line:
            a, b = [x.strip() for x in line.split("|", 1)]; links.append((a, b)); continue
        k, _, v = line.partition(":"); meta[k.strip()] = v.strip()
    return meta, links, entries


CSS = """
@font-face{font-family:N;src:url(/assets/Newsreader.woff2) format("woff2");font-weight:300 700;font-display:swap}
@font-face{font-family:N;font-style:italic;src:url(/assets/Newsreader-Italic.woff2) format("woff2");font-weight:300 700;font-display:swap}
:root{--paper:#eef0ed;--ink:#1f2a37;--body:#2a3542;--quiet:#44566b;--faint:#6f7f91;--rule:#d3d7d1;--blue:#3d5b78;--mark:#e4e9ee}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--body);font:400 18px/1.62 N,Georgia,"Songti SC","Noto Serif SC",serif;
  font-feature-settings:"onum" 1;text-rendering:optimizeLegibility}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:2;opacity:.05;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
.lamp{position:fixed;inset:0;pointer-events:none;z-index:0}
.wrap{position:relative;z-index:1;max-width:940px;margin:0 auto;padding:88px 32px 72px}
a{color:var(--blue);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px;text-decoration-color:rgba(61,91,120,.35);transition:text-decoration-color .2s}
a:hover{text-decoration-color:var(--blue)}
mark.todo{background:var(--mark);color:var(--quiet);font-style:italic;padding:0 .25em;border-radius:2px}
header{display:grid;grid-template-columns:112px 1fr 140px;gap:0 28px;align-items:start;margin-bottom:76px}
header .txt{grid-column:2}
h1{margin:0 0 .35rem;font-weight:500;font-size:2.35rem;line-height:1.1;color:var(--ink);letter-spacing:-.01em}
h1 .cn{font-size:1.05rem;font-weight:400;color:var(--faint);margin-left:.6rem;letter-spacing:.08em}
.tagline{margin:0 0 .3rem;color:var(--quiet);font-size:1.08rem;max-width:34rem}
.links{display:flex;gap:1.3rem;font-size:.95rem}
.links a{color:var(--quiet);text-decoration-color:rgba(68,86,107,.3)}
.reveal{font:inherit;color:var(--quiet);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px;text-decoration-color:rgba(68,86,107,.3)}
.avatar{grid-column:3;width:140px;height:140px;border-radius:50%;object-fit:cover;display:block;
  box-shadow:0 0 0 1px rgba(31,42,55,.06),0 6px 22px -12px rgba(31,42,55,.35)}
.tl{list-style:none;margin:0;padding:0}
.row{display:grid;grid-template-columns:112px minmax(0,1fr) 250px;gap:0 28px;padding:20px 0 22px;border-top:1px solid var(--rule)}
.row:last-child{border-bottom:1px solid var(--rule)}
.date{font-size:.9rem;color:var(--faint);padding-top:.18rem;font-variant-numeric:oldstyle-nums;letter-spacing:.02em;white-space:nowrap}
.main p{margin:0 0 .55rem}.main p:last-child{margin:0}
.traits{margin:0 0 1.1rem;color:var(--faint);font-size:.95rem;font-style:italic;letter-spacing:.01em}
.notes{align-self:start;margin-top:.2rem}
.note{font-style:italic;font-size:.9rem;line-height:1.55;color:var(--faint);padding-left:16px;border-left:1px solid var(--rule);
  transition:color .25s,border-color .25s;margin:0 0 .9rem}
.note:last-child{margin-bottom:0}
.pb{display:block;height:.5em}
.note .lab{font-style:normal;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:.1rem}
.row:hover .note{color:var(--quiet)}
.note.hot{color:var(--ink);border-left-color:var(--blue)}
.an{text-decoration:underline dotted;text-decoration-color:rgba(61,91,120,.55);text-underline-offset:4px;text-decoration-thickness:1px;cursor:default;transition:background .2s}
.an.hot{background:rgba(61,91,120,.08);border-radius:2px}
.why{display:none}
.hl{color:var(--ink);font-weight:500;-webkit-box-decoration-break:clone;box-decoration-break:clone;padding-bottom:3px;
  background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='6' viewBox='0 0 120 6'><path d='M0 3.6 C 14 2.2, 26 4.6, 40 3.2 S 66 2.0, 80 3.6 S 106 4.4, 120 2.8' fill='none' stroke='%233d5b78' stroke-opacity='.55' stroke-width='1.6' stroke-linecap='round'/></svg>") repeat-x left bottom/120px 6px}
.hl .an{text-decoration:none}
.em{color:var(--ink);font-weight:500}
.mark{color:var(--ink);font-weight:500;padding:.05em .35em;margin-left:-.35em;border-radius:3px 6px 4px 7px;
  background:linear-gradient(100deg,rgba(247,226,128,0) 0%,rgba(247,226,128,.78) 3%,rgba(247,226,128,.6) 50%,rgba(247,226,128,.75) 96%,rgba(247,226,128,0) 100%);
  -webkit-box-decoration-break:clone;box-decoration-break:clone}
.go{margin-top:.7rem!important}
.go a{font-weight:500;color:var(--blue);text-decoration-color:rgba(61,91,120,.5)}
footer{margin-top:56px;font-size:.85rem;color:var(--faint);padding-left:140px}
@media (max-width:760px){
  body{font-size:17px}
  .wrap{padding:44px 16px 56px}
  header{grid-template-columns:1fr;margin-bottom:44px}
  header .txt{grid-column:1}
  .avatar{grid-column:1;grid-row:1;width:96px;height:96px;margin-bottom:22px}
  h1{font-size:2rem}
  .row{grid-template-columns:1fr;padding:16px 0 18px}
  .date{margin-bottom:.25rem;padding:0}
  .notes{display:none;margin-top:.7rem}
  .row.open .notes{display:block}.row.open .note{color:var(--quiet)}
  .why{display:inline-block;margin-top:.45rem;font:italic .88rem N,serif;color:var(--faint);background:none;border:0;padding:0;cursor:pointer}
  .why::after{content:" +"}.row.open .why::after{content:" –"}
  footer{padding-left:0}
}
@media (hover:none),(prefers-reduced-motion:reduce){.lamp{display:none}}
.art{max-width:660px;margin:0 auto}
.back{font-size:.92rem;color:var(--quiet);text-decoration-color:rgba(68,86,107,.3)}
.art h1{margin:2.4rem 0 .6rem;font-size:2.1rem;line-height:1.15}
.art .meta{color:var(--faint);font-size:.92rem;margin:0 0 2.4rem;padding-bottom:1.4rem;border-bottom:1px solid var(--rule)}
.art .meta a{color:var(--quiet)}
.art h2{font-weight:500;font-size:1.3rem;color:var(--ink);margin:2.6rem 0 .8rem}
.art p{margin:0 0 1.1rem}
.art ul{margin:0 0 1.2rem;padding-left:1.2rem}.art li{margin:0 0 .45rem}
.art strong{font-weight:600;color:var(--ink)}
.art table{border-collapse:collapse;width:100%;margin:.4rem 0 1.4rem;font-size:.92rem;font-variant-numeric:lining-nums tabular-nums}
.art th{text-align:left;font-weight:500;color:var(--quiet);border-bottom:1px solid var(--quiet);padding:.4rem .6rem .4rem 0}
.art td{border-bottom:1px solid var(--rule);padding:.4rem .6rem .4rem 0}
.art .tw{overflow-x:auto}
"""

JS = """
const lamp=document.getElementById("lamp");
if(matchMedia("(hover:hover)").matches&&!matchMedia("(prefers-reduced-motion:reduce)").matches){
  let raf=0;addEventListener("pointermove",e=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{
    lamp.style.background=`radial-gradient(520px circle at ${e.clientX}px ${e.clientY}px, rgba(255,255,253,.8), rgba(255,255,253,0) 70%)`})});
}
document.querySelectorAll(".row").forEach(r=>{
  const pair=n=>[...r.querySelectorAll(`[data-n="${n}"]`)];
  r.querySelectorAll("[data-n]").forEach(el=>{
    el.addEventListener("mouseenter",()=>pair(el.dataset.n).forEach(x=>x.classList.add("hot")));
    el.addEventListener("mouseleave",()=>pair(el.dataset.n).forEach(x=>x.classList.remove("hot")));});
});
document.querySelectorAll(".reveal").forEach(b=>b.onclick=()=>{b.textContent="WeChat: "+b.dataset.v;try{navigator.clipboard.writeText(b.dataset.v);b.title="copied"}catch(e){}});
document.querySelectorAll(".why").forEach(b=>b.onclick=()=>{const r=b.closest(".row");r.classList.toggle("open");b.setAttribute("aria-expanded",r.classList.contains("open"))});
"""


def build():
    meta, links, entries = parse(os.path.join(HERE, "content.txt"))
    rows = []
    for e in entries:
        ps, k = [], 0
        for p in e["main"]:
            if p.startswith("-> "):
                ps.append(f'<p class="go">{inline(p[3:])}</p>'); continue
            t, k = anchors(inline(p), k); ps.append(f"<p>{t}</p>")
        main = "".join(ps)
        notes = []
        for i, nt in enumerate(e["note"]):
            lab = ""
            if len(e["note"]) > 1 and ": " in nt:
                l, _, nt = nt.partition(": "); lab = f'<span class="lab">{html.escape(l)}</span>'
            dn = f' data-n="{i}"' if i < k else ""
            notes.append(f'<p class="note"{dn}>{lab}{inline(nt, "note").replace(chr(10), "<span class=pb></span>")}</p>')
        why = '<button class="why" aria-expanded="false">more</button>' if notes else ""
        notehtml = f'<aside class="notes">{"".join(notes)}</aside>' if notes else ""
        dt = e["date"]; mk = dt.startswith("!"); dt = dt.lstrip("!").strip()
        dhtml = f'<span class="mark">{html.escape(dt)}</span>' if mk else html.escape(dt)
        rows.append(f'<li class="row"><div class="date">{dhtml}</div><div class="main">{main}{why}</div>{notehtml}</li>')
    def lk(a, u):
        if u.startswith("reveal:"):
            v = html.escape(u[7:])
            return f'<button class="reveal" data-v="{v}" title="click to show and copy">{html.escape(a)}</button>'
        return f'<a href="{html.escape(u)}">{html.escape(a)}</a>'
    linkhtml = "".join(lk(a, u) for a, u in links)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(meta.get('name',''))}</title>
<meta name="description" content="{html.escape(meta.get('tagline',''))}">
<link rel="preload" href="/assets/Newsreader.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style></head><body>
<div class="lamp" id="lamp"></div>
<div class="wrap">
<header><div class="txt"><h1>{html.escape(meta.get('name',''))}</h1>
<p class="tagline">{inline(meta.get('tagline',''))}</p>{('<p class="traits">' + ' · '.join(html.escape(x.strip()) for x in meta['traits'].split(',')) + '</p>') if meta.get('traits') else ''}<nav class="links">{linkhtml}</nav></div>
<img class="avatar" src="/assets/avatar.jpg" alt="{html.escape(meta.get('name',''))}" width="140" height="140"></header>
<ol class="tl">{''.join(rows)}</ol>
<footer>© 2026 {html.escape(meta.get('name',''))}</footer>
</div><script>{JS}</script></body></html>"""
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)


def md(text):
    out, para, lst, tbl = [], [], [], []
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
        if lst: out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + "</ul>"); lst.clear()
        if tbl:
            rows = [r for r in tbl if not set(r.replace("|", "").strip()) <= set("-: ")]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            h = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'); tbl.clear()
    for line in text.splitlines():
        if not line.strip(): flush(); continue
        if line.startswith("## "): flush(); out.append(f"<h2>{inline(line[3:])}</h2>"); continue
        if line.startswith("- "): lst.append(line[2:]); continue
        if line.startswith("|"): tbl.append(line); continue
        para.append(line.strip())
    flush(); return "".join(out)


def build_projects():
    pdir = os.path.join(HERE, "projects")
    for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if not f.endswith(".txt"): continue
        lines = open(os.path.join(pdir, f), encoding="utf-8").read().splitlines()
        title = lines[0].lstrip("# ").strip()
        meta = lines[1].partition(":")[2].strip() if lines[1].startswith("meta:") else ""
        body = md("\n".join(lines[2:]))
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · Zhuowei Li</title>
<link rel="preload" href="/assets/Newsreader.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style></head><body><div class="lamp" id="lamp"></div>
<div class="wrap"><article class="art"><a class="back" href="/">← Zhuowei Li</a>
<h1>{inline(title)}</h1><p class="meta">{inline(meta)}</p>{body}</article>
<footer style="padding-left:0;max-width:660px;margin:56px auto 0">© 2026 Zhuowei Li</footer></div><script>{JS}</script></body></html>"""
        d = os.path.join(pdir, f[:-4]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    build(); build_projects(); print("built index.html and project pages")
