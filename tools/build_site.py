# -*- coding: utf-8 -*-
"""吾妻大夢 Station を生成する。  python3 tools/build_site.py  をリポジトリ直下で実行。"""
import io, os, json, html, re
import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG   = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_layer.svg"), encoding="utf-8").read()

def esc(t): return html.escape(t, quote=True)

# 全ページ共通の索引（母港からすべての桟橋が見える）
NAV = [
  ("",          "Station",  "母港"),
  ("now/",      "Now",      "いま"),
  ("column/",   "Column",   "コラム"),
  ("works/books/",   "Books",   "小説"),
  ("works/poem/",    "Poem",    "詩"),
  ("works/tanka/",   "Tanka",   "短歌"),
  ("works/theater/", "Theater", "演劇"),
  ("works/app/",     "App",     "アプリ"),
  ("for-you/",  "For You",  "あなたへ"),
  ("contact/",  "Contact",  "連絡"),
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

def page(depth, path, title, desc, body, here, jsonld=None, ogtitle=None):
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

<img class="bg-base" src="@@U@@assets/bg.webp" alt="" aria-hidden="true" decoding="async">
@@BG@@

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
    }, {rootMargin:'0px 0px -6% 0px', threshold:0.05});
    for(var j=0;j<els.length;j++) io.observe(els[j]);
  }
})();
</script>
</body>
</html>
"""
    vals = dict(TITLE=esc(title), DESC=esc(desc), URL=url, U=u, ROOT=C.SITE_ROOT, BG=BG,
                BODY=body, INDEX=site_index(depth, here), LD=ld, FAV=fav,
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

def paras(text, cls="prose"):
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s: continue
        if s == "◯":
            out.append('    <div class="poem-mark">◯</div>'); continue
        ind = ' class="indent"' if line.startswith("　") else ""
        out.append('    <p%s>%s</p>' % (ind, esc(s)))
    return ('  <div class="readpanel reveal">\n    <div class="%s">\n%s\n    </div>\n  </div>'
            % (cls, "\n".join("  "+o for o in out)))

# ================================================================= ページ定義
AUTHOR_ID = C.SITE_ROOT + "#author"
PERSON = {"@type":"Person","@id":AUTHOR_ID,"name":"吾妻大夢","alternateName":"Hiromu Azuma",
          "jobTitle":"小説家","description":C.PROFILE,"url":C.SITE_ROOT,
          "sameAs":[C.X_URL, C.NOTE_URL]}

def build():
    made = []

    # ---------------------------------------------------------- Station
    body = []
    body.append('  <div class="wh">\n'
      '    <h1 class="wh-title"><span class="wh-jp">吾妻大夢</span><span class="wh-en">Station</span></h1>\n'
      '    <p class="wh-sub">Hiromu Azuma — Home Port</p>\n'
      '    <div class="wh-lead">\n      <p class="wh-lead-p">%s</p>\n'
      '      <div class="wh-rule"></div>\n      <p class="wh-bio">%s</p>\n    </div>\n  </div>'
      % (esc(C.LEAD), esc(C.BIO)))

    body.append(section("Now — いま", '  <div class="hub-grid">\n' + hub(
        "now/", "ゆいめ", "2026.08.18 最新作 / Novel · SF",
        "感情を直通させる管、CABLE。ことばに触れる、SF抒情。", "Kindle・ペーパーバックで発売中", wide=True) + '\n  </div>'))

    cols = "\n".join(hub("column/%s/" % s, jp, en, lede) for s, jp, en, lede, _ in C.COLUMN)
    body.append(section("Column — コラム", '  <div class="hub-grid">\n%s\n  </div>' % cols))

    body.append(section("Links", '  <div class="linkrow">\n'
        '    <a class="ext" href="%s" target="_blank" rel="noopener">X</a>\n'
        '    <a class="ext" href="%s" target="_blank" rel="noopener">note</a>\n  </div>' % (C.X_URL, C.NOTE_URL)))

    works = "\n".join([
      hub("works/books/",   "Books",   "小説",   "13の小説・詩集・エッセイ。マジックリアリズム幻想小説を中心に。", "みぎうで／灯花／絵喰い／Debris／錆びた平方／shuffle／shape／パラレルの耐用／Meltopia／ゆいめ／浸水地帯／Key"),
      hub("works/poem/",    "Poem",    "詩",     "感慨を織り重ねて描写する詩的掌編。", C.POEM_TITLE),
      hub("works/tanka/",   "Tanka",   "短歌",   "語と語の間に距離を置いた、二十五首の連作。", C.TANKA_TITLE),
      hub("works/theater/", "Theater", "演劇",   "%s %s。" % (C.THEATER["company"], C.THEATER["note"]), C.THEATER["title"]),
      hub("works/app/",     "App",     "アプリ", C.APP["lede"], "%s（%s）" % (C.APP["title"], C.APP["sub"])),
    ])
    body.append(section("Works — 作品", '  <div class="hub-grid">\n%s\n  </div>' % works))

    body.append(section("For You — あなたへ",
      '  <div class="readpanel reveal">\n    <p class="pull">%s</p>\n'
      '    <div class="linkrow" style="justify-content:center;margin-top:2rem">'
      '<a class="ext" href="for-you/">For You →</a></div>\n  </div>' % esc(C.FOR_YOU)))

    body.append(section("Contact — 連絡",
      '  <div class="linkrow reveal"><a class="ext" href="mailto:%s">%s</a></div>' % (C.EMAIL, C.EMAIL)))

    made.append(("index.html", page(0, "", "吾妻大夢 Station｜小説・詩・短歌・演劇・アプリ",
      "吾妻大夢（Hiromu Azuma）の母港。世界には不思議さがある。確からしさもある。その境目は、どこだろう？ 小説、詩、短歌、コラム、演劇、アプリケーション。",
      "\n".join(body), "", jsonld={"@context":"https://schema.org","@graph":[PERSON,
        {"@type":"WebSite","@id":C.SITE_ROOT+"#site","url":C.SITE_ROOT,"name":"吾妻大夢 Station",
         "inLanguage":"ja","author":{"@id":AUTHOR_ID}},
        {"@type":"ItemList","name":"Station","itemListElement":[
          {"@type":"ListItem","position":i+1,"name":en,"item":C.SITE_ROOT+path}
          for i,(path,en,jp) in enumerate(NAV) if path]}]})))

    # ---------------------------------------------------------- Now
    b = [crumbs(1, [(None,"Now")]), ph("Now", "いま — 最新作"),
         solo_card(C.YUIME, badge=C.YUIME["date"]),
         '  <div class="meta-row reveal" style="justify-content:center;margin-top:1.4rem">'
         '<span>%s</span><span>発売日 %s</span></div>' % (esc(C.YUIME["pages"]), esc(C.YUIME["date"]))]
    made.append(("now/index.html", page(1, "now/", "ゆいめ｜吾妻大夢 Station",
      "吾妻大夢の最新作『ゆいめ』。感情を直通させる管、CABLE。ことばに触れる、SF抒情。Kindle・ペーパーバックで発売中。",
      "\n".join(b), "now/", ogtitle="ゆいめ — 吾妻大夢 最新作")))

    # ---------------------------------------------------------- Column
    cards = "\n".join(hub("%s/" % s, jp, "%s — %s" % (en, jp), lede) for s, jp, en, lede, _ in C.COLUMN)
    b = [crumbs(1, [(None,"Column")]),
         ph("Column", "コラム", "考えていることを、そのまま置いています。"),
         '  <div class="hub-grid reveal">\n%s\n  </div>' % cards]
    made.append(("column/index.html", page(1, "column/", "Column｜吾妻大夢 Station",
      "吾妻大夢のコラム。天使、触診、接続——考えていることを、そのまま置いています。",
      "\n".join(b), "column/")))

    for slug, jp, en, lede, text in C.COLUMN:
        b = [crumbs(2, [("../","Column"), (None, jp)]),
             ph(en, jp, lede), paras(text, "prose"),
             '  <div class="prose-end"></div>']
        made.append(("column/%s/index.html" % slug, page(2, "column/%s/" % slug,
          "%s｜Column｜吾妻大夢 Station" % jp, lede, "\n".join(b), "column/",
          ogtitle="%s — 吾妻大夢" % jp,
          jsonld={"@context":"https://schema.org","@type":"Article","headline":jp,
                  "alternativeHeadline":en,"description":lede,"inLanguage":"ja",
                  "author":PERSON,"mainEntityOfPage":C.SITE_ROOT+"column/%s/" % slug})))

    # ---------------------------------------------------------- Works hub
    works = "\n".join([
      hub("books/",   "Books",   "小説",   "13の小説・詩集・エッセイ。"),
      hub("poem/",    "Poem",    "詩",     C.POEM_TITLE),
      hub("tanka/",   "Tanka",   "短歌",   C.TANKA_TITLE),
      hub("theater/", "Theater", "演劇",   C.THEATER["title"]),
      hub("app/",     "App",     "アプリ", "%s（%s）" % (C.APP["title"], C.APP["sub"])),
    ])
    b = [crumbs(1, [(None,"Works")]), ph("Works", "作品", "書いたもの、つくったもの。"),
         '  <div class="hub-grid reveal">\n%s\n  </div>' % works]
    made.append(("works/index.html", page(1, "works/", "Works｜吾妻大夢 Station",
      "吾妻大夢の作品。小説、詩、短歌、演劇、アプリケーション。", "\n".join(b), "works/books/")))

    # ---------------------------------------------------------- Books
    b = [crumbs(2, [("../","Works"), (None,"Books")]),
         ph("Books", "小説・詩集・エッセイ", "Amazon KDPにて発売中。")]
    b.append(section("Latest", solo_card(C.YUIME, badge=C.YUIME["date"])))
    b.append(section("Novel — Set editions", "\n".join(set_block(*s) for s in C.SETS)))
    b.append(section("Novel — Single", solo_card(C.MELTOPIA)))
    b.append(section("Essay & Poetry", solo_card(C.SHINSUI) + "\n" + solo_card(C.KEY)))
    books_ld = [{"@type":"ListItem","position":i+1,"item":{"@type":"Book","name":n,"author":{"@id":AUTHOR_ID},
                 "inLanguage":"ja","url":AMZ % a}} for i,(n,a) in enumerate(
                 [(C.YUIME["title"],C.YUIME["kindle"])] +
                 [(c["title"],c["asin"]) for s in C.SETS for c in s[3]] +
                 [(C.MELTOPIA["title"],C.MELTOPIA["asin"]),(C.SHINSUI["title"],C.SHINSUI["asin"]),(C.KEY["title"],C.KEY["asin"])])]
    made.append(("works/books/index.html", page(2, "works/books/", "Books｜吾妻大夢 Station",
      "吾妻大夢の小説・詩集・エッセイ一覧。マジックリアリズム幻想小説、思索小説を中心に、Amazon KDPにて発売中。",
      "\n".join(b), "works/books/", jsonld={"@context":"https://schema.org","@type":"ItemList",
      "name":"吾妻大夢 作品一覧","itemListElement":books_ld})))

    # ---------------------------------------------------------- Poem
    b = [crumbs(2, [("../","Works"), (None,"Poem")]),
         ph("Poem", "詩 — %s" % C.POEM_TITLE, "感慨を織り重ねて描写する詩的掌編。"),
         paras(C.POEM, "poem"),
         '  <div class="prose-end"></div>\n'
         '  <div class="linkrow reveal" style="justify-content:center;margin-top:2rem">'
         '<a class="ext" href="%s" target="_blank" rel="noopener">Kindle版</a></div>' % (AMZ % C.POEM_ASIN)]
    made.append(("works/poem/index.html", page(2, "works/poem/", "空力の考察｜Poem｜吾妻大夢 Station",
      "吾妻大夢の詩的掌編『空力の考察』全文。感慨を織り重ねて描写する。", "\n".join(b), "works/poem/",
      ogtitle="空力の考察 — 吾妻大夢",
      jsonld={"@context":"https://schema.org","@type":"CreativeWork","name":C.POEM_TITLE,
              "genre":"詩","inLanguage":"ja","author":PERSON})))

    # ---------------------------------------------------------- Tanka
    groups = [g.strip() for g in C.TANKA.split("\n\n") if g.strip()]
    inner = []
    for gi, g in enumerate(groups):
        lines = "\n".join('      <div class="tanka">%s</div>' % esc(l) for l in g.split("\n"))
        rule = '\n      <div class="tanka-rule"></div>' if gi < len(groups)-1 else ""
        inner.append('    <div class="tanka-group">\n%s%s\n    </div>' % (lines, rule))
    b = [crumbs(2, [("../","Works"), (None,"Tanka")]),
         ph("Tanka", "短歌 — %s" % C.TANKA_TITLE, "二十五首の連作。"),
         '  <div class="readpanel reveal">\n    <div class="tanka-set">\n%s\n    </div>\n  </div>' % "\n".join(inner)]
    made.append(("works/tanka/index.html", page(2, "works/tanka/", "ディクショナリ｜Tanka｜吾妻大夢 Station",
      "吾妻大夢の短歌連作『ディクショナリ』二十五首。", "\n".join(b), "works/tanka/",
      ogtitle="ディクショナリ — 吾妻大夢 短歌",
      jsonld={"@context":"https://schema.org","@type":"CreativeWork","name":C.TANKA_TITLE,
              "genre":"短歌","inLanguage":"ja","author":PERSON})))

    # ---------------------------------------------------------- Theater
    t = C.THEATER
    b = [crumbs(2, [("../","Works"), (None,"Theater")]),
         ph("Theater", "演劇 — %s" % t["title"]),
         '  <div class="solo-wrap reveal">\n    <div class="solo-card">\n      <div class="solo-body">\n'
         '        <div class="c-tag">Theater · %s</div><h2 class="c-title">%s</h2>\n'
         '        <div class="c-div"></div>\n'
         '        <p class="c-desc">%s %s。</p>\n'
         '        <div class="c-links"><a class="c-link" href="%s" target="_blank" rel="noopener">本編を観る</a>'
         '<a class="c-link" href="%s" target="_blank" rel="noopener">劇団チャンネル</a></div>\n'
         '      </div>\n    </div>\n  </div>'
         % (esc(t["note"]), esc(t["title"]), esc(t["company"]), esc(t["note"]), t["url"], t["channel"])]
    made.append(("works/theater/index.html", page(2, "works/theater/", "デジカ｜Theater｜吾妻大夢 Station",
      "『デジカ』京田辺、演劇ないん会 第16回本公演。本編映像を公開中。", "\n".join(b), "works/theater/",
      ogtitle="デジカ — 京田辺、演劇ないん会")))

    # ---------------------------------------------------------- App
    a = C.APP
    pts = "\n".join('    <p>%s</p>' % esc(x) for x in a["points"])
    b = [crumbs(2, [("../","Works"), (None,"App")]),
         ph("App", "アプリ — %s（%s）" % (a["title"], a["reading"]), a["lede"]),
         '  <div class="readpanel reveal">\n    <p class="pull">%s</p>\n'
         '    <div class="prose-end"></div>\n'
         '    <div class="prose" style="margin-top:2.4rem">\n%s\n    </div>\n  </div>' % (esc(a["principle"]), pts),
         '  <div class="linkrow reveal" style="justify-content:center;margin-top:2.4rem">'
         '<a class="ext" href="%s" target="_blank" rel="noopener">接鳴をひらく →</a></div>' % a["url"]]
    made.append(("works/app/index.html", page(2, "works/app/", "接鳴｜App｜吾妻大夢 Station",
      "接鳴（せつめい）— 電子焚火。音のオブジェクトを配置し、その位置関係だけで音楽が組み上がるインタラクティブ楽器。",
      "\n".join(b), "works/app/", ogtitle="接鳴 — 電子焚火")))

    # ---------------------------------------------------------- For You
    b = [crumbs(1, [(None,"For You")]), ph("For You", "あなたへ"),
         '  <div class="readpanel reveal" style="margin-top:1rem">\n    <p class="pull">%s</p>\n  </div>' % esc(C.FOR_YOU),
         '  <div class="prose-end"></div>']
    made.append(("for-you/index.html", page(1, "for-you/", "For You｜吾妻大夢 Station",
      "絶望にひたされていても、どこかにはずみはあるはずで。吾妻大夢から、あなたへ。",
      "\n".join(b), "for-you/", ogtitle="For You — 吾妻大夢")))

    # ---------------------------------------------------------- Contact
    b = [crumbs(1, [(None,"Contact")]), ph("Contact", "連絡", "ご感想、ご依頼、なんでもどうぞ。"),
         '  <div class="linkrow reveal" style="justify-content:center">'
         '<a class="ext" href="mailto:%s">%s</a></div>' % (C.EMAIL, C.EMAIL),
         '  <div class="linkrow reveal" style="justify-content:center;margin-top:1rem">'
         '<a class="ext" href="%s" target="_blank" rel="noopener">X</a>'
         '<a class="ext" href="%s" target="_blank" rel="noopener">note</a></div>' % (C.X_URL, C.NOTE_URL),
         '  <div class="ph-lead reveal" style="text-align:center;margin-top:2.6rem">%s</div>' % esc(C.PROFILE)]
    made.append(("contact/index.html", page(1, "contact/", "Contact｜吾妻大夢 Station",
      "吾妻大夢への連絡先。メール、X、note。", "\n".join(b), "contact/")))

    total = 0
    for path, text in made:
        n = write(path, text); total += n
        print("  %-34s %6.1f KB" % (path, n/1024.0))
    print("%d ページ / 合計 %.1f KB" % (len(made), total/1024.0))

if __name__ == "__main__":
    build()
