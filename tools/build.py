#!/usr/bin/env python3
"""Builds the static JTIMS site from the scraped source pages (tools/*.html).
Titles/authors are copied verbatim from the original site."""
import re, html, os, shutil, json
from html import escape as e

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', 'site')
DOCS = os.path.join(SITE, 'docs')
RAW = os.path.join(DOCS)  # original hashed pdfs live here on first run

ISSUES = [
    dict(slug='jlitt-vol-1-issue-1', src='p_jlitt-vol-1-issue-1.html', series='JLITT', vol='Volume I, Issue I',
         name='Journal of Library & Information Technology Trends (JLITT)', label='Vol I No I 2015', year='2015', cover='cover-jlitt.jpg', kind='lines1'),
    dict(slug='jlitt-vol-1-issue-2', src='j2.html', series='JLITT', vol='Volume I, Issue II',
         name='Journal of Library & Information Technology Trends (JLITT)', label='Vol I No II 2017', year='2017', cover='cover-jlitt.jpg', kind='lines1'),
    dict(slug='jlitt-vol-3-issue-1', src='j3.html', series='JLITT', vol='Volume III, Issue I',
         name='Journal of Library & Information Technology Trends (JLITT)', label='Vol III No I 2018', year='2018', cover='cover-jlitt.jpg',
         kind=[1, 2, 2, 2, 1, 1, 1, 2, 2]),
    dict(slug='jtim-vol-1-issue-1', src='p_jtim-vol-i-issue-i.html', series='J-TIM', vol='Volume I, Issue I',
         name='Journal of Library Technology and Information Management (J-TIM)', label='Vol I No I 2025', year='2025', cover='cover-jtim.jpg', kind='lines1'),
    dict(slug='jtim-vol-2-issue-1', src='p_jtim-vol-ii-issue-i.html', series='J-TIM', vol='Volume II, Issue I',
         name='Journal of Library Technology and Information Management (J-TIM)', label='Vol II No I 2025', year='2025', cover='cover-jtim.jpg', kind='lines1'),
]

def slugify(s, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:n].rstrip('-')

def parse(issue):
    raw = open(os.path.join(HERE, issue['src']), encoding='utf8').read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    s = re.sub(r'<a [^>]*href="([^"]*(?:filesusr|doi\.org)[^"]*)"[^>]*>', r'\n[[LINK \1]]\n', s)
    s = re.sub(r'<(br|/p|/h\d|/li|/div)[^>]*>', '\n', s)
    t = html.unescape(re.sub(r'<[^>]+>', '', s)).replace('​', '').replace('\xa0', ' ')
    t = re.sub(r'\n\s*\n+', '\n', t)
    body = t[t.find('Use tab'):t.find('Your Academic Partner')]
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    # drop header lines up to the volume/label line
    start = next(i for i, l in enumerate(lines) if l.startswith(('Vol I', 'Volume')))
    lines = lines[start + 1:]
    lines = [l for l in lines if l != 'Journal of Technology and Information Management']
    arts, block, doi = [], [], None
    for l in lines:
        m = re.match(r'\[\[LINK (.*)\]\]', l)
        if m:
            u = m.group(1)
            if 'doi.org' in u:
                doi = u
            else:
                arts.append((block, doi, u)); block, doi = [], None
        elif re.match(r'^(https://doi\.org/)?10\.5281/zenodo\.\d+$', l):
            doi = 'https://doi.org/' + l.replace('https://doi.org/', '')  # DOI text as displayed on the original page
        else:
            block.append(l)
    out = []
    for i, (blk, doi, url) in enumerate(arts):
        k = issue['kind'][i] if isinstance(issue['kind'], list) else 1
        title = ' '.join(blk[:k]); authors = ' '.join(blk[k:]).rstrip(',').strip()
        out.append(dict(title=title, authors=authors, doi=doi, pdf=url))
    return out

# ------------------------------------------------------------------ data
for iss in ISSUES:
    iss['articles'] = parse(iss)
    for n, a in enumerate(iss['articles'], 1):
        old = os.path.basename(a['pdf'])
        new = f"{iss['slug']}-{n:02d}-{slugify(a['title'])}.pdf"
        for cand in (old, new):
            p = os.path.join(DOCS, cand)
            if os.path.exists(p):
                if cand != new: os.rename(p, os.path.join(DOCS, new))
                break
        else:
            raise SystemExit('missing pdf ' + old)
        a['file'] = new
        a['size'] = os.path.getsize(os.path.join(DOCS, new))

TEAM = [
    ('Prof E.J. Ottong', 'Editor-in-chief', ''),
    ('Prof. Aniebiet I.Ntui', 'Editorial Board', ''),
    ('Prof. Ruth S. Bassey', 'Editorial Board', ''),
    ('Prof. Nkoyo Edem', 'Editorial Board', ''),
    ('Prof. Afebende', 'Editorial Board', ''),
    ('Dr. Isu Matthew Egbe', 'Managing Editor', ''),
    ('Prof. William Nkanu', 'Editorial Board', ''),
    ('Dr. James A. Odu', 'Editorial Board', ''),
    ('Dr. Imelda B. Edam- Agbor', 'Managing Editor', ''),
    ('Dr. Blessing E. Ogunjimi', 'Managing Editor', ''),
]
DEPT = 'Department of Library and Information Science'
UNI = 'University of Calabar'

# ------------------------------------------------------------------ shell
SERIES = 'Journal of Technology and Information Management Series'
NAV = [('index.html', 'Home'), ('journals.html', 'Journals'), ('jtim-vol-1-issue-1.html', 'JTIM Vol I, Issue I'),
       ('jtim-vol-2-issue-1.html', 'JTIM Vol II, Issue I'), ('jlitt-vol-1-issue-1.html', 'JLITT Vol I, Issue I')]

def size(n):
    return f"{n/1048576:.1f} MB" if n >= 1048576 else f"{round(n/1024)} KB"

def page(title, body, active, desc=''):
    nav = ''.join(f'<a href="{h}"{" class=on" if h == active else ""}>{e(t)}</a>' for h, t in NAV)
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'Peer-reviewed publications in library and information science, University of Calabar.')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="wrap bar">
<a class="brand" href="index.html"><img src="assets/logo.svg" alt="" width="40" height="40"><span>{e(SERIES)}</span></a>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
<nav>{nav}<a class="cta" href="submit.html">Submit Manuscript</a></nav>
</div></header>
<main>{body}</main>
<footer><div class="wrap fgrid">
<div><div class="fbrand">Journal of Technology and Information Management</div><p>Your Academic Partner</p></div>
<div><h4>Contact</h4><p><a href="tel:+2348039399051">+2348039399051</a><br><a href="tel:+2348035049914">+2348035049914</a><br><a href="mailto:info@jtims.com">info@jtims.com</a></p>
<p>Mary Slessor Ave, University of Calabar, Calabar 540281,<br>Cross River State, Nigeria</p></div>
<div><h4>Explore</h4><p><a href="journals.html">All journals</a><br><a href="jtim-vol-1-issue-1.html">JTIM Vol I, Issue I</a><br><a href="jtim-vol-2-issue-1.html">JTIM Vol II, Issue I</a><br><a href="jlitt-vol-1-issue-1.html">JLITT Vol I, Issue I</a><br><a href="submit.html">Submit Manuscript</a></p></div>
</div><div class="wrap copy">© 2025 by Journal of Technology and Information Management.</div></footer>
<script src="assets/site.js"></script>
</body></html>'''

def issue_by(slug):
    return next(i for i in ISSUES if i['slug'] == slug)

def issue_card(i):
    return f'''<a class="icard" href="{i['slug']}.html"><img src="img/{i['cover']}" alt="Cover of {e(i['name'])}" loading="lazy">
<div><span class="tag">{e(i['vol'])}</span><h3>{e(i['name'])}</h3><p>{e(i['label'])}</p>
<span class="more">View Articles <i>→</i></span></div></a>'''

# ------------------------------------------------------------------ home
def initials(n):
    w = [x for x in re.sub(r'^(Prof\.?|Dr\.?)\s+', '', n).split() if x[0].isalpha()]
    return (w[0][0] + w[-1][0]).upper()

team = ''.join(f'''<li class="member"><h3>{e(n)}</h3><span class="role">{e(r)}</span>
<p>{DEPT}, {UNI}</p></li>''' for n, r, _ in TEAM)

home = f'''
<section class="hero"><div class="wrap hgrid"><div>
<p class="eyebrow">{e(SERIES)}</p>
<h1>Elevate Your Research</h1>
<p class="lead">Join us in fostering research and innovation through peer-reviewed publications that contribute to the academic community.</p>
<div class="btns"><a class="btn pri" href="submit.html">Submit Your Manuscript</a><a class="btn" href="journals.html">Latest Research Updates</a></div>
</div><div class="hcov"><img class="c2" src="img/cover-jlitt.jpg" alt="JLITT cover"><img class="c1" src="img/cover-jtim.jpg" alt="J-TIM cover"></div></div></section>
<section class="stats"><div class="wrap sgrid"><div><b>2</b><span>Journals</span></div><div><b>5</b><span>Issues</span></div><div><b>{sum(len(i['articles']) for i in ISSUES)}</b><span>Articles</span></div><div><b>DOI</b><span>Integrated library</span></div></div></section>
<section class="sec"><div class="wrap">
<div class="head"><h2>Explore Our Journals</h2><p>Your gateway to cutting-edge research and insights.</p></div>
<div class="two">
<article class="jcard"><img src="img/cover-jlitt.jpg" alt="JLITT cover"><div><h3>Journal of Library and Information Technology Trends (JLITT)</h3>
<p>JLITT explores the latest developments and trends where library science meets information technology, serving as a forum for insights on their impact on information services and professional practice.</p>
<a class="btn pri" href="journals.html#jlitt">View More</a></div></article>
<article class="jcard"><img src="img/cover-jtim.jpg" alt="J-TIM cover"><div><h3>Journal of Library Technology and Information Management (J-TIM)</h3>
<p>J-TIM is a peer-reviewed publication focusing on the strategic management of technology in libraries, covering topics like digital preservation, automation, and data management.</p>
<a class="btn pri" href="journals.html#jtim">View More</a></div></article>
</div></div></section>
<section class="sec alt" id="team"><div class="wrap">
<div class="head"><p class="eyebrow">The Team</p><h2>Dedication. Expertise. Passion.</h2></div>
<ul class="team">{team}</ul></div></section>
<section class="vision" id="vision"><div class="wrap vgrid"><div class="vimg"><img src="img/shelf.jpg" alt="" loading="lazy"></div><div>
<p class="eyebrow">Our Vision</p><h2>Harnessing Academic Excellence</h2>
<p>At the Journal of Technology and Information Management, we facilitate peer-reviewed publications that benefit researchers and readers alike. Our platform supports manuscript submissions, tracks peer review processes, and maintains a comprehensive journal library integrated with DOI. We aim to cultivate a vibrant scholarly environment within the Library and Information Science sector.</p>
<a class="btn pri" href="journals.html">Learn More</a></div></div></section>
'''

# ------------------------------------------------------------------ journals
def group(series):
    return ''.join(issue_card(i) for i in ISSUES if i['series'] == series)

journals = f'''
<section class="phead"><div class="wrap"><p class="eyebrow">Library</p><h1>Journals</h1><p class="lead">Every volume and issue, with full-text PDFs.</p></div></section>
<section class="sec"><div class="wrap">
<div id="jlitt" class="head left"><h2>Journal of Library &amp; Information Technology Trends <small>(JLITT)</small></h2></div>
<div class="igrid">{group('JLITT')}</div>
<div id="jtim" class="head left sp"><h2>Journal of Library Technology and Information Management <small>(J-TIM)</small></h2></div>
<div class="igrid">{group('J-TIM')}</div>
</div></section>'''

# ------------------------------------------------------------------ issue pages
def art(i, n, a):
    doi = f'<a class="doi" href="{e(a["doi"])}" target="_blank" rel="noopener">{e(a["doi"])}</a>' if a['doi'] else ''
    return f'''<article class="art" data-q="{e((a['title'] + ' ' + a['authors']).lower())}"><span class="num">{n:02d}</span>
<div class="abody"><h3><a href="docs/{a['file']}" target="_blank" rel="noopener">{e(a['title'])}</a></h3><p class="au">{e(a['authors'])}</p>{doi}</div>
<a class="dl" href="docs/{a['file']}" target="_blank" rel="noopener" title="Open PDF in a new tab"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0l-5-5m5 5l5-5M4 21h16"/></svg><span>PDF<em>{size(a['size'])}</em></span></a></article>'''

def issue_page(i):
    idx = ISSUES.index(i)
    prev = f'<a href="{ISSUES[idx-1]["slug"]}.html">← {e(ISSUES[idx-1]["vol"])} ({ISSUES[idx-1]["series"]})</a>' if idx else '<span></span>'
    nxt = f'<a href="{ISSUES[idx+1]["slug"]}.html">{e(ISSUES[idx+1]["vol"])} ({ISSUES[idx+1]["series"]}) →</a>' if idx < len(ISSUES) - 1 else '<span></span>'
    arts = ''.join(art(i, n, a) for n, a in enumerate(i['articles'], 1))
    return f'''
<section class="phead issue"><div class="wrap ih"><img src="img/{i['cover']}" alt="Cover"><div>
<p class="eyebrow"><a href="journals.html">Journals</a> / {e(i['vol'])}</p>
<h1>{e(i['name'])}</h1><p class="lead">{e(i['label'] if i['series']=='JLITT' else i['vol'] + ' · ' + i['label'])} · {len(i['articles'])} articles</p></div></div></section>
<section class="sec"><div class="wrap narrow">
<div class="tools"><input id="q" type="search" placeholder="Search titles or authors…" aria-label="Search articles"><span id="count">{len(i['articles'])} articles</span></div>
<div class="alist">{arts}</div><p id="none" hidden>No articles match your search.</p>
<div class="pn">{prev}{nxt}</div></div></section>'''

# ------------------------------------------------------------------ submit
submit = '''
<section class="phead"><div class="wrap"><p class="eyebrow">For authors</p><h1>Submit Manuscript</h1><p class="lead">Join us in fostering research and innovation through peer-reviewed publications that contribute to the academic community.</p></div></section>
<section class="sec"><div class="wrap narrow">
<form id="sf" class="form" action="mailto:info@jtims.com" method="post" enctype="text/plain">
<label>Full name<input name="Name" required></label>
<label>Email<input name="Email" type="email" required></label>
<label>Journal<select name="Journal"><option>Journal of Library Technology and Information Management (J-TIM)</option><option>Journal of Library &amp; Information Technology Trends (JLITT)</option></select></label>
<label>Manuscript title<input name="Title" required></label>
<label>Message<textarea name="Message" rows="5"></textarea></label>
<button class="btn pri" type="submit">Submit Your Manuscript</button>
<p class="note">This opens your email app addressed to <a href="mailto:info@jtims.com">info@jtims.com</a>. Please attach your manuscript file.</p>
</form></div></section>'''

# ------------------------------------------------------------------ write
def w(name, content):
    open(os.path.join(SITE, name), 'w', encoding='utf8').write(content)

w('index.html', page('Home | Journal of Technology and Information Management Series', home, 'index.html'))
w('journals.html', page('Journals | Journal of Technology and Information Management Series', journals, 'journals.html'))
for i in ISSUES:
    w(i['slug'] + '.html', page(f"{i['vol']} | {i['name']}", issue_page(i), i['slug'] + '.html' if i['slug'] in [n[0][:-5] for n in NAV] else 'journals.html'))
w('submit.html', page('Submit Manuscript | Journal of Technology and Information Management Series', submit, 'submit.html'))
json.dump([{k: v for k, v in i.items() if k != 'kind'} for i in ISSUES], open(os.path.join(HERE, 'data.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print('built', sum(len(i['articles']) for i in ISSUES), 'articles')
