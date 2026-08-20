# -*- coding: utf-8 -*-
"""吾妻大夢 Station を生成する。  python3 tools/build_site.py  をリポジトリ直下で実行。"""
import io, os, json, html, re
import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG   = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_layer.svg"), encoding="utf-8").read()

def esc(t): return html.escape(t, quote=True)

# 全ページ共通の索引（母港からすべての桟橋が見える）
NAV = [
  ("",         "Station", "母港"),
  ("#column",  "Column",  "コラム"),
  ("works/",   "Works",   "作品"),
  ("contact/", "Contact", "連絡"),
]

def up(depth): return "../" * depth

def crumbs(depth, trail):
    """trail: [(相対リンク or None, 表示名)] — 最後の要素が現在地"""
    out = ['<a href="%s">吾妻大夢 Station</a>' % (up(depth) or "./")]
    for i, (href, name) in enumerate(trail):
        out.append('<span class="topbar-sep">/</span>')
        if href is None or i == len(trail) - 1:
            out.append('<span class="topbar-here">%s</span>' % esc(name))
        else:
            out.append('<a href="%s">%s</a>' % (href, esc(name)))
    return '<nav class="topbar">\n  ' + "\n  ".join(out) + '\n</nav>'

def site_index(depth, here):
    items = []
    for path, en, jp in NAV:
        cls = ' class="here"' if path == here else ''
        items.append('<a href="%s%s"%s>%s</a>' % (up(depth), path, cls, esc(en)))
    return ('<nav class="site-index">\n  <div class="si-label">STATION</div>\n'
            '  <div class="si-list">\n    %s\n  </div>\n</nav>' % "\n    ".join(items))

def page(depth, path, title, desc, body, here, jsonld=None, ogtitle=None, back=None):
    u   = up(depth)
    url = C.SITE_ROOT + path
    ld  = ('\n<script type="application/ld+json">\n%s\n</script>'
           % json.dumps(jsonld, ensure_ascii=False, indent=1)) if jsonld else ""
    fav = ("data:image/svg+xml,%3Csvg%20xmlns%3D'http%3A//www.w3.org/2000/svg'%20viewBox%3D'0%200%2032%2032'%3E"
           "%3Crect%20width%3D'32'%20height%3D'32'%20fill%3D'%23f7f8fb'/%3E%3Cg%20fill%3D'none'%20stroke%3D'%231a1a2e'%3E"
           "%3Crect%20x%3D'5.5'%20y%3D'5.5'%20width%3D'21'%20height%3D'21'%20stroke-width%3D'1.7'/%3E"
           "%3Crect%20x%3D'10.5'%20y%3D'10.5'%20width%3D'11'%20height%3D'11'%20stroke-width%3D'1.2'/%3E"
           "%3Crect%20x%3D'14.5'%20y%3D'14.5'%20width%3D'3'%20height%3D'3'%20stroke-width%3D'0.9'/%3E%3C/g%3E%3C/svg%3E")
    tmpl = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>@@TITLE@@</title>
<meta name="description" content="@@DESC@@">
<link rel="canonical" href="@@URL@@">
<meta name="author" content="吾妻大夢">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#f7f8fb">
<link rel="icon" href="@@FAV@@">

<meta property="og:type" content="website">
<meta property="og:site_name" content="吾妻大夢 Station">
<meta property="og:title" content="@@OGTITLE@@">
<meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@URL@@">
<meta property="og:image" content="@@ROOT@@assets/ogp.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="@@OGTITLE@@">
<meta name="twitter:description" content="@@DESC@@">
<meta name="twitter:image" content="@@ROOT@@assets/ogp.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Noto+Serif+JP:wght@300;400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="@@U@@assets/site.css">@@LD@@
</head>
<body>
<script>document.documentElement.className+=" js";</script>
<div class="progress"></div>

<div class="bg-layer bg-base"><img src="@@U@@assets/bg.webp" alt="" aria-hidden="true" decoding="async"></div>
<div class="bg-layer bg-c">@@BG@@</div>

<div class="container">
@@BODY@@
@@INDEX@@
  <div class="wf">© Hiromu Azuma</div>
</div>

<script>
(function(){
  var root=document.documentElement, queued=false;
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function update(){
    queued=false;
    var y=window.pageYOffset||0;
    var max=Math.max(1, document.documentElement.scrollHeight-window.innerHeight);
    root.style.setProperty('--sp', Math.min(1,y/max).toFixed(4));
    var h=Math.min(1, y/460);
    root.style.setProperty('--hero-o', (1-h*0.9).toFixed(3));
    root.style.setProperty('--hero-t', (h*-72).toFixed(2));
    root.style.setProperty('--hero-s', (1-h*0.06).toFixed(4));
  }
  if(!reduce){
    addEventListener('scroll', function(){ if(!queued){queued=true; requestAnimationFrame(update);} }, {passive:true});
    addEventListener('resize', update, {passive:true});
    update();
  }
  var els=document.querySelectorAll('.reveal');
  if(reduce || !('IntersectionObserver' in window)){
    for(var i=0;i<els.length;i++) els[i].classList.add('in');
  } else {
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
    }, {rootMargin:'0px 0px -6% 0px', threshold:0});
    for(var j=0;j<els.length;j++) io.observe(els[j]);
  }
})();
</script>
</body>
</html>
"""
    title   = C.SITE_TITLE          # 全ページ共通。余計な説明は付けない
    ogtitle = C.SITE_TITLE
    desc    = C.SITE_DESC
    if back is None and depth > 0:
        back = "../"          # どのページも「ひとつ上」へ戻る
    backhtml = ('  <div class="back-wrap"><a class="backlink" href="%s" aria-label="ひとつ上へ戻る" title="戻る">←</a></div>'
                % back) if back else ""
    vals = dict(TITLE=esc(title), DESC=esc(desc), URL=url, U=u, ROOT=C.SITE_ROOT, BG=BG,
                BODY=body + ("\n" + backhtml if backhtml else ""),
                INDEX=site_index(depth, here), LD=ld, FAV=fav,
                OGTITLE=esc(ogtitle or title))
    for k, v in vals.items():
        tmpl = tmpl.replace("@@" + k + "@@", v)
    return tmpl

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8").write(text)
    return len(text.encode())

COVER = "https://images-na.ssl-images-amazon.com/images/P/%s.09.LZZZZZZZ"
AMZ   = "https://www.amazon.co.jp/dp/%s"

def hub(href, en, jp, desc, items=None, wide=False):
    it = '\n      <div class="hub-items">%s</div>' % esc(items) if items else ""
    return ('    <a class="hub-card%s" href="%s">\n'
            '      <div class="hub-top"><span class="hub-en">%s</span><span class="hub-arrow">→</span></div>\n'
            '      <div class="hub-jp">%s</div>\n'
            '      <div class="hub-desc">%s</div>%s\n'
            '    </a>' % (" hub-wide" if wide else "", href, esc(en), esc(jp), esc(desc), it))

def section(label, inner, reveal=True):
    r = " reveal" if reveal else ""
    return ('  <div class="section">\n    <div class="section-label%s">%s</div>\n%s\n  </div>' % (r, esc(label), inner))

def solo_card(b, extra_links=None, badge=None, cover_key="asin"):
    links = []
    if b.get("kindle"): links.append('<a class="c-link" href="%s" target="_blank" rel="noopener">Kindle</a>' % (AMZ % b["kindle"]))
    if b.get("paper"):  links.append('<a class="c-link" href="%s" target="_blank" rel="noopener">Paperback</a>' % (AMZ % b["paper"]))
    if b.get("asin"):   links.append('<a class="c-link" href="%s" target="_blank" rel="noopener">%s</a>' % (AMZ % b["asin"], b.get("label","Kindle")))
    for t,u in (extra_links or []): links.append('<a class="c-link" href="%s" target="_blank" rel="noopener">%s</a>' % (u, esc(t)))
    toc = ('\n          <div class="toc-sep"></div>\n          <p class="toc">%s</p>' % esc(b["toc"])) if b.get("toc") else ""
    head = ('      <div class="new-head"><span class="new-badge">New</span><span class="new-date">%s</span></div>\n' % esc(badge)) if badge else ""
    return ('    <div class="solo-wrap%s reveal">\n%s'
            '      <div class="solo-card">\n'
            '        <div class="cover-wrap"><img src="%s" alt="%s" loading="lazy"></div>\n'
            '        <div class="solo-body">\n'
            '          <div class="c-tag">%s</div><h2 class="c-title">%s</h2>\n'
            '          <div class="c-div"></div>\n'
            '          <p class="c-desc">%s</p>%s\n'
            '          <div class="c-links">%s</div>\n'
            '        </div>\n      </div>\n    </div>'
            % (" new-wrap" if badge else "", head, COVER % (b.get("cover") or b["asin"]), esc(b["title"]),
               esc(b["tag"]), esc(b["title"]), esc(b["desc"]), toc, "".join(links)))

def set_block(label, pb, abstract, cards):
    inner = []
    for c in cards:
        inner.append('        <div class="set-card">\n'
                     '          <div class="card-inner">\n'
                     '            <div class="cover-sm"><img src="%s" alt="%s" loading="lazy"></div>\n'
                     '            <div class="card-body"><div class="c-tag">%s</div><h2 class="c-title">%s</h2></div>\n'
                     '          </div>\n          <div class="c-div"></div>\n'
                     '          <p class="c-desc">%s</p>\n'
                     '          <div class="c-links"><a class="c-link" href="%s" target="_blank" rel="noopener">Kindle</a></div>\n'
                     '        </div>' % (COVER % c["asin"], esc(c["title"]), esc(c["tag"]), esc(c["title"]),
                                         esc(c["desc"]), AMZ % c["asin"]))
    return ('    <div class="set-wrap reveal">\n'
            '      <div class="set-header">\n        <div class="set-label">%s</div>\n'
            '        <div class="set-header-top">\n          <p class="set-abstract">%s</p>\n'
            '          <div class="set-pb-block">\n            <div class="set-pb-label">二篇収録・ペーパーバック</div>\n'
            '            <a class="pb-btn" href="%s" target="_blank" rel="noopener">Paperback →</a>\n'
            '          </div>\n        </div>\n      </div>\n'
            '      <div class="set-grid">\n%s\n      </div>\n    </div>'
            % (esc(label), esc(abstract), AMZ % pb, "\n".join(inner)))

def ph(en, jp, lead=None):
    l = '\n    <p class="ph-lead">%s</p>' % esc(lead) if lead else ""
    return ('  <div class="ph reveal">\n    <span class="ph-en">%s</span>\n'
            '    <span class="ph-jp">%s</span>%s\n  </div>' % (esc(en), esc(jp), l))

def case_body(text):
    """[Case:xxx] を部、《題》を詩題、詩の途中の空行だけを連の切れ目として組む。"""
    out, open_verse, has_line, pending_gap = [], False, False, False
    def close():
        if open_verse: out.append('    </div>\n  </div>')
    for raw in text.split("\n"):
        st = raw.strip()
        if st.startswith("[Case:"):
            close(); open_verse = has_line = pending_gap = False
            out.append('  <div class="case-part"><span>%s</span></div>'
                       % esc(st.strip("[]").replace(":", " : ")))
        elif st.startswith("《") and st.endswith("》"):
            close()
            out.append('  <div class="verse">\n    <h2 class="verse-title">%s</h2>\n    <div class="verse-body">'
                       % esc(st[1:-1]))
            open_verse, has_line, pending_gap = True, False, False
        elif not st:
            if open_verse and has_line:
                pending_gap = True          # 本文が続く場合だけ連の切れ目にする
        else:
            if pending_gap:
                out.append('      <div class="verse-gap"></div>')
                pending_gap = False
            out.append('      <p class="verse-line">%s</p>' % esc(st))
            has_line = True
    close()
    return '  <div class="readpanel reveal">\n%s\n  </div>' % "\n".join("  "+o for o in out)

def paras(text, cls="prose"):
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s: continue
        if s == "◯":
            out.append('    <div class="poem-mark">◯</div>'); continue
        ind = ' class="indent"' if (cls == "prose" or line.startswith("　")) else ""
        out.append('    <p%s>%s</p>' % (ind, esc(s)))
    return ('  <div class="readpanel reveal">\n    <div class="%s">\n%s\n    </div>\n  </div>'
            % (cls, "\n".join("  "+o for o in out)))

# ================================================================= アイコン
ICONS = {
 "tenshi": '<svg class="ico" viewBox="0 0 48 48" aria-hidden="true">'
   '<ellipse cx="24" cy="11" rx="8.5" ry="3.4" class="g"/>'
   '<path d="M6 41 C12 25 19 20 24 20 C29 20 36 25 42 41"/>'
   '<path d="M13 41 C17 30 20.5 26 24 26 C27.5 26 31 30 35 41" class="d"/>'
   '<circle cx="24" cy="20" r="1.6" class="f"/></svg>',
 "shokushin": '<svg class="ico" viewBox="0 0 48 48" aria-hidden="true">'
   '<circle cx="24" cy="20" r="11"/>'
   '<line x1="4" y1="31" x2="44" y2="31"/>'
   '<circle cx="24" cy="31" r="2" class="f"/>'
   '<path d="M13 36 Q24 41 35 36" class="d"/>'
   '<path d="M8 41 Q24 48 40 41" class="d"/></svg>',
 "setsuzoku": '<svg class="ico" viewBox="0 0 48 48" aria-hidden="true">'
   '<line x1="10" y1="13" x2="24" y2="25"/><line x1="24" y1="25" x2="39" y2="11"/>'
   '<line x1="24" y1="25" x2="11" y2="38"/><line x1="24" y1="25" x2="38" y2="37"/>'
   '<line x1="10" y1="13" x2="39" y2="11" class="d"/>'
   '<circle cx="24" cy="25" r="3" class="f"/>'
   '<circle cx="10" cy="13" r="2.3"/><circle cx="39" cy="11" r="2.3"/>'
   '<circle cx="11" cy="38" r="2.3"/><circle cx="38" cy="37" r="2.3"/></svg>',
 "poem": '<svg class="ico" viewBox="0 0 48 48" aria-hidden="true">'
   '<path d="M4 17 Q12 8 20 17 T36 17 T52 17"/>'
   '<path d="M4 25 Q12 16 20 25 T36 25 T52 25" class="g"/>'
   '<path d="M4 33 Q12 24 20 33 T36 33 T52 33" class="d"/></svg>',
 "tanka": '<svg class="ico" viewBox="0 0 48 48" aria-hidden="true">'
   '<line x1="14" y1="10" x2="34" y2="10"/>'
   '<line x1="10" y1="19" x2="38" y2="19" class="g"/>'
   '<line x1="14" y1="28" x2="34" y2="28"/>'
   '<line x1="10" y1="37" x2="38" y2="37" class="g"/>'
   '<line x1="10" y1="44" x2="38" y2="44"/></svg>',
}

# ================================================================= ページ定義
AUTHOR_ID = C.SITE_ROOT + "#author"
PERSON = {"@type":"Person","@id":AUTHOR_ID,"name":"吾妻大夢","alternateName":"Hiromu Azuma",
          "jobTitle":"小説家","description":C.PROFILE,"url":C.SITE_ROOT,
          "sameAs":[C.X_URL, C.NOTE_URL, C.YT_URL]}
P = C.PHRASE

# --- 外部リンクのアイコン ---
SOCIAL_SVG = {
 "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.67l7.73-8.84L1.25 2.25h6.83l4.71 6.23zm-1.16 17.52h1.83L7.08 4.13H5.12z"/></svg>',
 "note": '<svg viewBox="0 0 24 24" class="stroked" aria-hidden="true">'
         '<rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5"/>'
         '<path d="M8.6 16.4V9.1c1.6-1.1 3.2-1.6 4.6-1.6 1.6 0 2.4.9 2.4 2.6v6.3"/></svg>',
 "youtube": '<svg viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M23.5 7.2a3 3 0 0 0-2.1-2.1C19.5 4.6 12 4.6 12 4.6s-7.5 0-9.4.5A3 3 0 0 0 .5 7.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-4.8zM9.6 15.6V8.4l6.3 3.6z"/></svg>',
}
def social(depth=0):
    return ('    <div class="icon-links reveal">\n'
            '      <a class="ilink" href="%s" target="_blank" rel="noopener" aria-label="X" title="X">%s</a>\n'
            '      <a class="ilink" href="%s" target="_blank" rel="noopener" aria-label="note" title="note">%s</a>\n'
            '      <a class="ilink" href="%s" target="_blank" rel="noopener" aria-label="YouTube" title="YouTube">%s</a>\n'
            '    </div>' % (C.X_URL, SOCIAL_SVG["x"], C.NOTE_URL, SOCIAL_SVG["note"],
                            C.YT_URL, SOCIAL_SVG["youtube"]))

def label(en, phrase, anchor=None):
    a = ' id="%s"' % anchor if anchor else ""
    sub = '<span class="sl-sub">%s</span>' % esc(phrase) if phrase else ""
    return ('    <div class="section-label reveal"%s><span class="sl-en">%s</span>%s</div>'
            % (a, esc(en), sub))

def sect(en, phrase, inner, anchor=None):
    return '  <div class="section">\n%s\n%s\n  </div>' % (label(en, phrase, anchor), inner)

def col_row(href, title, sub, icon=None):
    return ('      <a class="col-row" href="%s">%s<span class="col-title">%s</span>'
            '<span class="col-sub">%s</span><span class="col-arrow">→</span></a>'
            % (href, ICONS.get(icon, ""), esc(title), esc(sub)))

def mini(href, title, desc, external=False, icon=None, thumb=None, depth=1):
    tgt = ' target="_blank" rel="noopener"' if external else ""
    if thumb:
        vis = '<img class="mini-thumb" src="%sassets/%s" alt="%s" loading="lazy">' % (up(depth), thumb, esc(title))
    elif icon:
        vis = '<span class="mini-plate">%s</span>' % ICONS[icon]
    else:
        vis = ""
    return ('      <a class="mini" href="%s"%s>%s<span class="mini-title">%s</span>'
            '<span class="mini-desc">%s</span><span class="mini-arrow">%s</span></a>'
            % (href, tgt, vis, esc(title), esc(desc), "↗" if external else "→"))

def wcard(href, en, phrase, visual, items, external=False, major=False, lead=None):
    tgt = ' target="_blank" rel="noopener"' if external else ""
    ld = '\n        <div class="wcard-lead">%s</div>' % esc(lead) if lead else ""
    return ('      <a class="wcard%s" href="%s"%s>\n'
            '        <div class="wcard-top"><span class="wcard-en">%s</span><span class="hub-arrow">%s</span></div>\n'
            '        <div class="wcard-phrase">%s</div>\n'
            '        <div class="wcard-visual%s">%s</div>%s\n'
            '        <div class="wcard-items">%s</div>\n      </a>'
            % (" wcard-major" if major else "", href, tgt, esc(en), "↗" if external else "→",
               esc(phrase), " jumble" if major else "", visual, ld, items))

def cv(asin, depth=1):  return '<img class="cv" src="%s" alt="" loading="lazy">' % (COVER % asin)
def sh(name, depth=1):  return '<img class="sh" src="%sassets/%s" alt="" loading="lazy">' % (up(depth), name)

def build():
    made = []

    # ============================================================ Station
    b = ['  <div class="wh">\n'
         '    <h1 class="wh-title"><span class="wh-jp">吾妻大夢</span><span class="wh-en">Station</span></h1>\n'
         '    <div class="wh-lead">\n      <p class="wh-lead-p">%s</p>\n'
         '      <div class="wh-rule"></div>\n      <p class="wh-bio">%s</p>\n    </div>\n  </div>'
         % (esc(C.LEAD), esc(C.BIO))]

    b.append(sect("Now", P["now"], solo_card(C.YUIME, badge=C.YUIME["date"]), anchor="now"))

    rows = "\n".join(col_row("column/%s/" % slug, jp, lede, icon=slug)
                     for slug, jp, en, lede, _ in C.COLUMN)
    b.append(sect("Column", P["column"],
        '    <div class="col-list reveal">\n%s\n    </div>' % rows, anchor="column"))

    b.append(sect("Links", P["links"], social(0), anchor="links"))

    # Works — 色々な作品の要素をひとつのカードに
    bits = [
      ('<img class="cv" src="%s" alt="" loading="lazy">' % (COVER % "B0HFNHM1B7"), "-7deg"),
      ('<span class="plate">%s</span>' % ICONS["tanka"], "5deg"),
      ('<img class="cv" src="%s" alt="" loading="lazy">' % (COVER % "B0B12RN7ZN"), "-3deg"),
      ('<img class="sh" src="assets/thumb-dejika.webp" alt="" loading="lazy">', "4deg"),
      ('<img class="cv" src="%s" alt="" loading="lazy">' % (COVER % "B0GFWDKKJY"), "-5deg"),
      ('<span class="plate">%s</span>' % ICONS["poem"], "6deg"),
      ('<img class="sh" src="assets/thumb-setsumei.webp" alt="" loading="lazy">', "-4deg"),
      ('<img class="cv" src="%s" alt="" loading="lazy">' % (COVER % "B0F9VCQNRV"), "3deg"),
    ]
    strip = "".join('<span style="--r:%s">%s</span>' % (r, h) for h, r in bits)
    b.append(sect("Works", P["works"],
        '    <a class="collage reveal" href="works/">\n'
        '      <div class="collage-strip">%s</div>\n'
        '      <div class="collage-bottom"><span class="wcard-en">Works</span>'
        '<span class="hub-arrow">→</span></div>\n'
        '      <div class="wcard-items">Books ／ Poem ／ Tanka ／ Theater ／ App</div>\n'
        '    </a>' % strip, anchor="works"))

    b.append(sect("For You", P["for_you"],
        '    <div class="whisper-wrap reveal">\n      <p class="whisper">%s</p>\n    </div>' % esc(C.FOR_YOU),
        anchor="for-you"))

    b.append(sect("Contact", "",
        '    <div class="linkrow reveal"><a class="ext" href="mailto:%s">%s</a></div>' % (C.EMAIL, C.EMAIL),
        anchor="contact"))

    made.append(("index.html", page(0, "", "吾妻大夢 Station｜小説・詩・短歌・演劇・アプリ",
      "吾妻大夢（Hiromu Azuma）の母港。世界には不思議さがある。確からしさもある。その境目は、どこだろう？ 小説を軸に、詩、短歌、コラム、演劇、アプリケーション。",
      "\n".join(b), "", jsonld={"@context":"https://schema.org","@graph":[PERSON,
        {"@type":"WebSite","@id":C.SITE_ROOT+"#site","url":C.SITE_ROOT,"name":"吾妻大夢 Station",
         "inLanguage":"ja","author":{"@id":AUTHOR_ID}}]})))

    # ============================================================ Column（各記事のみ。索引ページは置かない）
    for slug, jp, en, lede, text in C.COLUMN:
        snippet = text.replace("\n","").replace("　","")[:95] + "…"
        b = [crumbs(2, [(None, jp)]), ph(jp, en, lede), paras(text, "prose")]
        made.append(("column/%s/index.html" % slug, page(2, "column/%s/" % slug,
          jp, snippet, "\n".join(b), "#column", back="../../",
          ogtitle="%s — %s" % (jp, lede),
          jsonld={"@context":"https://schema.org","@type":"Article","headline":jp,
                  "alternativeHeadline":en,"description":lede,"inLanguage":"ja",
                  "author":PERSON,"mainEntityOfPage":C.SITE_ROOT+"column/%s/" % slug})))

    # ============================================================ Works（5つを同階層に）
    cards = [
      wcard("books/", "Books", P["books"],
            '<span class="jumble-mark"></span>' + "".join(
              '<span style="--r:%s"><img src="%s" alt="" loading="lazy"></span>' % (r, COVER % a)
              for a, r in [("B0HFNHM1B7","-7deg"),("B0B12RN7ZN","5deg"),("B0B7Z1D5YD","-3deg"),
                           ("B0BWT14YM1","4deg"),("B0C576Q4CT","-5deg"),("B0FPCZ39NC","6deg"),
                           ("B0GFWDKKJY","-4deg"),("B0F9VCQNRV","3deg")]),
            "小説・詩集・エッセイ 13冊 — ゆいめ／みぎうで／灯花／絵喰い／Debris／錆びた平方／shuffle／shape／パラレルの耐用／Meltopia／浸水地帯／Key",
            major=True, lead=C.BOOKS_LEAD),
      wcard("poem/", "Poem", P["poem"], '<span class="wplate">%s</span>' % ICONS["poem"], "空力の考察／Case — 詩的掌編と連作、二作。"),
      wcard("tanka/", "Tanka", P["tanka"], '<span class="wplate">%s</span>' % ICONS["tanka"], "ディクショナリ／戯画 — 二十五首の連作、二作。"),
      wcard("theater/", "Theater", P["theater"], sh("thumb-dejika.webp"),
            "デジカ — 京田辺、演劇ないん会 第16回本公演。脚本/演出：吾妻"),
      wcard("app/", "App", P["app"], sh("thumb-setsumei.webp") + sh("thumb-croqkey.webp"),
            "接鳴 -電子焚火- ／ CroqKey"),
    ]
    b = [crumbs(1, [(None,"Works")]), ph("Works", "作品", P["works"]),
         '  <div class="wgrid reveal">\n%s\n  </div>' % "\n".join(cards)]
    made.append(("works/index.html", page(1, "works/", "Works｜吾妻大夢 Station",
      "吾妻大夢の作品。小説、詩、短歌、演劇、アプリケーション。", "\n".join(b), "works/")))

    # ============================================================ Books
    shelf = [solo_card(C.YUIME, badge=C.YUIME["date"])]
    shelf += [set_block(*st) for st in C.SETS]
    shelf.append(solo_card(C.MELTOPIA))
    shelf.append(solo_card(C.SHINSUI))
    shelf.append(solo_card(C.KEY))
    b = [crumbs(2, [("../","Works"), (None,"Books")]),
         ph("Books", "小説・詩集・エッセイ", P["books"]), "\n".join(shelf)]
    books_ld = [{"@type":"ListItem","position":i+1,"item":{"@type":"Book","name":n,"author":{"@id":AUTHOR_ID},
                 "inLanguage":"ja","url":AMZ % a}} for i,(n,a) in enumerate(
                 [(C.YUIME["title"],C.YUIME["kindle"])] +
                 [(c["title"],c["asin"]) for st in C.SETS for c in st[3]] +
                 [(C.MELTOPIA["title"],C.MELTOPIA["asin"]),(C.SHINSUI["title"],C.SHINSUI["asin"]),(C.KEY["title"],C.KEY["asin"])])]
    made.append(("works/books/index.html", page(2, "works/books/", "Books｜吾妻大夢 Station",
      "吾妻大夢の小説・詩集・エッセイ一覧。マジックリアリズム幻想小説、思索小説を中心に、Amazon KDPにて発売中。",
      "\n".join(b), "works/", ogtitle="Books — %s" % P["books"],
      jsonld={"@context":"https://schema.org","@type":"ItemList","name":"吾妻大夢 作品一覧",
              "itemListElement":books_ld})))

    # ============================================================ Poem（索引）
    minis = "\n".join(mini("%s/" % w["slug"], w["title"], w["note"], icon="poem", depth=2)
                      for w in C.POEM_WORKS)
    b = [crumbs(2, [("../","Works"), (None,"Poem")]), ph("Poem", "詩", P["poem"]),
         '  <div class="reveal">\n%s\n  </div>' % minis]
    made.append(("works/poem/index.html", page(2, "works/poem/", "Poem｜吾妻大夢 Station",
      "吾妻大夢の詩。空力の考察、Case。", "\n".join(b), "works/",
      ogtitle="Poem — %s" % P["poem"])))

    for w in C.POEM_WORKS:
        body = case_body(w["text"]) if w["kind"] == "case" else paras(w["text"], "poem")
        b = [crumbs(3, [("../../","Works"), ("../","Poem"), (None, w["title"])]),
             ph(w["title"], "Poem", P["poem"]), body]
        if w["asin"]:
            b.append('  <div class="linkrow reveal" style="justify-content:center;margin-top:2.2rem">'
                     '<a class="ext" href="%s" target="_blank" rel="noopener">Kindle版</a></div>' % (AMZ % w["asin"]))
        made.append(("works/poem/%s/index.html" % w["slug"], page(3, "works/poem/%s/" % w["slug"],
          "%s｜Poem｜吾妻大夢 Station" % w["title"],
          "吾妻大夢の詩『%s』全文。" % w["title"], "\n".join(b), "works/",
          ogtitle="%s — %s" % (w["title"], P["poem"]),
          jsonld={"@context":"https://schema.org","@type":"CreativeWork","name":w["title"],
                  "genre":"詩","inLanguage":"ja","author":PERSON})))

    # ============================================================ Tanka
    minis = "\n".join(mini("%s/" % w["slug"], w["title"], w["note"], icon="tanka", depth=2)
                      for w in C.TANKA_WORKS)
    b = [crumbs(2, [("../","Works"), (None,"Tanka")]), ph("Tanka", "短歌", P["tanka"]),
         '  <div class="reveal">\n%s\n  </div>' % minis]
    made.append(("works/tanka/index.html", page(2, "works/tanka/", "Tanka｜吾妻大夢 Station",
      "吾妻大夢の短歌。ディクショナリ、戯画。", "\n".join(b), "works/",
      ogtitle="Tanka — %s" % P["tanka"])))

    for w in C.TANKA_WORKS:
        groups = [g.strip() for g in w["text"].split("\n\n") if g.strip()]
        inner = []
        for gi, g in enumerate(groups):
            lines = "\n".join('        <div class="tanka">%s</div>' % esc(l) for l in g.split("\n"))
            rule = '\n        <div class="tanka-rule"></div>' if gi < len(groups)-1 else ""
            inner.append('      <div class="tanka-group">\n%s%s\n      </div>' % (lines, rule))
        n = sum(len(g.split("\n")) for g in groups)
        b = [crumbs(3, [("../../","Works"), ("../","Tanka"), (None, w["title"])]),
             ph(w["title"], "Tanka", P["tanka"]),
             '  <div class="readpanel tanka-panel reveal">\n    <div class="tanka-set">\n%s\n    </div>\n  </div>' % "\n".join(inner)]
        made.append(("works/tanka/%s/index.html" % w["slug"], page(3, "works/tanka/%s/" % w["slug"],
          "%s｜Tanka｜吾妻大夢 Station" % w["title"],
          "吾妻大夢の短歌連作『%s』%d首。" % (w["title"], n), "\n".join(b), "works/",
          ogtitle="%s — %s" % (w["title"], P["tanka"]),
          jsonld={"@context":"https://schema.org","@type":"CreativeWork","name":w["title"],
                  "genre":"短歌","inLanguage":"ja","author":PERSON})))

    # ============================================================ Theater
    t = C.THEATER
    b = [crumbs(2, [("../","Works"), (None,"Theater")]), ph(t["title"], "Theater", P["theater"]),
         '  <div class="solo-wrap reveal">\n    <div class="solo-card">\n'
         '      <div class="cover-wrap"><img src="../../assets/thumb-dejika.webp" alt="%s" loading="lazy" style="width:150px"></div>\n'
         '      <div class="solo-body">\n'
         '        <div class="c-tag">Theater · %s</div><h2 class="c-title">%s</h2>\n'
         '        <div class="c-div"></div>\n        <p class="c-desc">%s</p>\n'
         '        <p class="c-desc">%s %s。\n%s</p>\n'
         '        <div class="c-links"><a class="c-link" href="%s" target="_blank" rel="noopener">本編を観る</a></div>\n'
         '      </div>\n    </div>\n  </div>'
         % (esc(t["title"]), esc(t["note"]), esc(t["title"]), esc(t["blurb"]),
            esc(t["company"]), esc(t["note"]), esc(t["credit"]), t["url"])]
    made.append(("works/theater/index.html", page(2, "works/theater/", "デジカ｜Theater｜吾妻大夢 Station",
      "『デジカ』京田辺、演劇ないん会 第16回本公演。脚本/演出：吾妻。本編映像を公開中。", "\n".join(b), "works/",
      ogtitle="デジカ — %s" % P["theater"], back="../")))

    # ============================================================ App
    b = [crumbs(2, [("../","Works"), (None,"App")]), ph("App", "アプリ", P["app"])]
    for i, a in enumerate(C.APPS):
        b.append('  <div class="solo-wrap reveal"%s>\n    <div class="solo-card">\n'
            '      <div class="cover-wrap"><img src="../../assets/%s" alt="%s" loading="lazy" style="width:150px"></div>\n'
            '      <div class="solo-body">\n        <div class="c-tag">App</div>'
            '<h2 class="c-title">%s</h2>\n        <div class="c-div"></div>\n'
            '        <p class="c-desc">%s</p>\n'
            '        <div class="c-links"><a class="c-link" href="%s" target="_blank" rel="noopener">ひらく</a></div>\n'
            '      </div>\n    </div>\n  </div>'
            % (' style="margin-top:1.6rem"' if i else "", a["thumb"], esc(a["title"]),
               esc(a["title"]), esc(a["desc"]), a["url"]))
    made.append(("works/app/index.html", page(2, "works/app/", "App｜吾妻大夢 Station",
      "接鳴 -電子焚火- と CroqKey。吾妻大夢のアプリケーション。", "\n".join(b), "works/",
      ogtitle="App — %s" % P["app"], back="../")))

    # ============================================================ Contact
    b = [crumbs(1, [(None,"Contact")]), ph("Contact", "連絡", "ご感想、ご依頼、なんでもどうぞ。"),
         '  <div class="linkrow reveal" style="justify-content:center">'
         '<a class="ext" href="mailto:%s">%s</a></div>' % (C.EMAIL, C.EMAIL),
         '  <div style="display:flex;justify-content:center;margin-top:1.2rem">\n%s\n  </div>' % social(1),
         '  <div class="ph-lead reveal" style="text-align:center;margin-top:2.6rem">%s</div>' % esc(C.PROFILE)]
    made.append(("contact/index.html", page(1, "contact/", "Contact｜吾妻大夢 Station",
      "吾妻大夢への連絡先。メール、X、note、YouTube。", "\n".join(b), "contact/")))

    total = 0
    for path, text in made:
        n = write(path, text); total += n
        print("  %-34s %6.1f KB" % (path, n/1024.0))
    print("%d ページ / 合計 %.1f KB" % (len(made), total/1024.0))

if __name__ == "__main__":
    build()
