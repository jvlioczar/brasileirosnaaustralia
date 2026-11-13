# Brasileiros na Austrália para IAs e buscadores: as listas são montadas por JavaScript, que muitos robôs não rodam.
#   llms.txt            índice em Markdown (padrão llmstxt.org): o que é o site, cada seção e os números
#   llms-full.txt       todo o conteúdo em português, em Markdown
#   llms-full-en.txt    todo o conteúdo em inglês
#   JSON-LD             bloco entre <!-- seo:start --> e <!-- seo:end --> no index.html: WebSite, WebPage e as listas
#                       (criadores, agências, apps, perfis, cidades, guia como HowTo, FAQ como FAQPage, dicionário como DefinedTermSet)
#   Atualizado em       data visível no rodapé, entre <!-- upd:start --> e <!-- upd:end -->, e a chave kupd do I18N
#   sitemap.xml         lastmod de hoje
# Lê os dados rodando o index.html no Chrome sem janela, nas duas línguas. Rode de novo (python tools/llms.py)
# sempre que mudar criadores, agências, apps, perfis, guia, cidades, fatos, dicionário ou vídeos.
import re, os, json, html as H, subprocess, tempfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://brasileirosnaaustralia.biblioverse.org/'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
INDEX = os.path.join(ROOT, 'index.html')
TODAY = datetime.date.today().isoformat()
PUBLISHED = '2026-10-14'  # primeira publicação no GitHub Pages
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

EXPORT = r'''
window.__BNA=function(lang){LANG=lang;renderAll();return{
 creators:creators.map(c=>({...c,cityL:c.city?tC(c.city):"",typesL:c.types.map(tT)})),
 agencies,
 apps:APPS.map(([c,items])=>[tA(c),items.map(([n,d,u])=>[tA(n),tA(d),u]).sort((a,b)=>a[0].localeCompare(b[0],lang,{sensitivity:"base"}))]),
 profiles:PROFILES.map(([c,l])=>[tP(c),l]),
 dict:DICT,facts:FACTS,
 reels:REELS.map((r,i)=>[EN()&&REELS_EN[i]||r[0],r[1]]).filter(r=>r[1]),
 cities:CITYDATA.map((c,i)=>{const e=CITY_EN[i];const g=k=>EN()?e[k]:c[k];return{n:c.n,c:c.c,st:c.st,rent:c.rent,sum:c.sum,win:c.win,pop:g("pop"),reg:g("reg"),pro:g("pro"),con:g("con"),bom:g("bom"),s:c.s}})
}};
'''

DUMP = r'''<pre id="o"></pre><script>
const inl=el=>[...el.childNodes].map(n=>n.nodeType===3?n.textContent:n.nodeType!==1?"":n.tagName==="A"?`[${n.textContent.trim()}](${n.href})`:n.tagName==="B"||n.tagName==="STRONG"?`**${inl(n).trim()}**`:inl(n)).join("").replace(/\s+/g," ");
function md(el){const o=[];for(const c of el.children){const t=c.tagName;
  if(t==="H4")o.push("#### "+inl(c).trim());
  else if(t==="UL"||t==="OL")o.push([...c.children].map(li=>"- "+inl(li).trim()).join("\n"));
  else if(t==="DIV"&&c.classList.contains("phones"))o.push([...c.children].map(x=>`- **${txt(x.querySelector("b"))}**: ${txt(x.querySelector("span"))}`).join("\n"));
  else if(t==="DIV"&&[...c.children].some(x=>/^(H4|P|UL|OL|DIV)$/.test(x.tagName)))o.push(md(c));
  else{const s=inl(c).trim();if(s)o.push(s)}}
  return o.filter(Boolean).join("\n\n")}
const txt=el=>el?inl(el).trim():"";
const out={};
for(const lang of ["pt","en"]){
  const d=window.__BNA(lang);
  d.title=document.title;
  d.lede=txt(document.querySelector(".hero .lede"));
  d.lede2=txt(document.querySelector(".hero .lede2"));
  d.footer=[...document.querySelectorAll("footer .wrap > span")].map(txt);
  d.sec={};
  document.querySelectorAll("main section").forEach(s=>{d.sec[s.id]={h:txt(s.querySelector("h2")),p:txt(s.querySelector(".sh p")),
    notes:[...s.querySelectorAll(".costbox p.src, .popcard p.src")].map(txt),
    src:[...s.querySelectorAll(".fsrc a")].map(a=>[a.textContent.trim(),a.href])}});
  d.tabs=Object.fromEntries([...document.querySelectorAll(".tab")].map(t=>[t.dataset.tab,t.textContent.trim()]));
  d.guide=[...document.querySelectorAll("#guide details")].map(x=>({t:txt(x.querySelector("summary h3")),s:txt(x.querySelector("summary p")),
    h:[...x.querySelectorAll(".leg-body h4")].map(txt),body:md(x.querySelector(".leg-body"))}));
  d.join=[txt(document.querySelector("#criadores .join h3")),txt(document.querySelector("#criadores .join p"))];
  d.notice=txt(document.querySelector("#criadores .notice"));
  d.faqh=txt(document.querySelector("#faq h3"));d.faqp=txt(document.querySelector("#faq .faq-note"));
  d.faq=[...document.querySelectorAll("#faq details")].map(x=>[txt(x.querySelector("summary")),txt(x.querySelector("p"))]);
  d.about={label:txt(document.querySelector("#sobre .about-id .label")),name:txt(document.querySelector("#sobre .about-id h2")),
    role:txt(document.querySelector("#sobre .role")),body:[...document.querySelectorAll("#sobre .about-body > p:not(.label)")].map(txt)};
  out[lang]=d;
}
document.getElementById("o").textContent=JSON.stringify(out);
</script>'''


def load():
    s = open(INDEX, encoding='utf-8').read()
    i = s.rindex('\n})();\n</script>')
    s = s[:i] + EXPORT + s[i:]
    s = s.replace('</body>', DUMP + '</body>', 1)
    page = os.path.join(tempfile.gettempdir(), 'bna-dump.html')
    open(page, 'w', encoding='utf-8').write(s)
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--allow-file-access-from-files',
                        '--virtual-time-budget=5000', '--dump-dom', 'file:///' + page.replace('\\', '/')],
                       capture_output=True, encoding='utf-8')
    m = re.search(r'<pre id="o">(.*?)</pre>', r.stdout, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit('O Chrome não devolveu os dados. stderr:\n' + r.stderr[-2000:])
    return json.loads(H.unescape(m.group(1)))


D = load()
P, E = D['pt'], D['en']
ig = lambda h: f'https://www.instagram.com/{h}/'
TAB_ORDER = ['criadores', 'agencias', 'apps', 'fatos', 'cidades', 'guia', 'dicionario', 'reels', 'sobre']

W = {'pt': {'url': BASE, 'nocity': 'Cidade indefinida', 'aussie': 'australiano de coração brasileiro',
            'office': 'escritório na Austrália', 'focus': 'foco na Austrália', 'apps': 'Apps e serviços', 'profiles': 'Perfis',
            'rent': 'Aluguel de apartamento por semana', 'pop': 'População', 'max': 'Máxima em janeiro e julho',
            'visa': 'Visto', 'jobs': 'Emprego', 'br': 'Comunidade brasileira', 'pro': 'A favor', 'con': 'Contra',
            'good': 'Bom para', 'src': 'Fontes', 'stats': 'Números', 'popcities': 'Cidades mais populosas',
            'step': 'Etapa', 'watch': 'Vídeo', 'other': 'Outra língua',
            'full_other': f'[Full content in English]({BASE}llms-full-en.txt)'},
     'en': {'url': BASE + '?lang=en', 'nocity': 'City to be confirmed', 'aussie': 'Australian with a Brazilian heart',
            'office': 'office in Australia', 'focus': 'Australia focus', 'apps': 'Apps and services', 'profiles': 'Accounts',
            'rent': 'Unit rent per week', 'pop': 'Population', 'max': 'Max temperature in January and July',
            'visa': 'Visa', 'jobs': 'Jobs', 'br': 'Brazilian community', 'pro': 'Pros', 'con': 'Cons',
            'good': 'Good for', 'src': 'Sources', 'stats': 'Key numbers', 'popcities': 'Most populous cities',
            'step': 'Step', 'watch': 'Video', 'other': 'Other language',
            'full_other': f'[Conteúdo completo em português]({BASE}llms-full.txt)'}}


def anchor(lang, tab): return W[lang]['url'] + '#' + tab


def creators_by_city(d, lang):
    groups = {}
    for c in d['creators']:
        groups.setdefault(c['cityL'] or '', []).append(c)
    keys = sorted((k for k in groups if k), key=lambda k: (-len(groups[k]), k)) + ([''] if '' in groups else [])
    return [(k or W[lang]['nocity'], groups[k]) for k in keys]


def creator_line(c, lang):
    extra = f", {W[lang]['aussie']}" if c['au'] else ''
    return f"- [{c['name']}]({ig(c['handle'])}) @{c['handle']}: {', '.join(c['typesL'])}{extra}"


def badge(b, lang): return {2: W[lang]['office'], 1: W[lang]['focus']}.get(b, '')


def full(d, lang):
    w, s = W[lang], d['sec']
    sec = lambda k: f"## {s[k]['h']}\n\n{s[k]['p']}\n\nLink: {anchor(lang, k)}"
    srcs = lambda k: (f"\n\n### {w['src']}\n\n" + '\n'.join(f'- [{t}]({u})' for t, u in s[k]['src'])) if s[k]['src'] else ''
    name = 'Brasileiros na Austrália' if lang == 'pt' else 'Brasileiros na Austrália (Brazilians in Australia)'
    out = [f"# {name}", '', f"> {d['lede']}", '', d['lede2'], '',
           f"{w['other']}: {w['full_other']}. " + ' '.join(d['footer'][1:]), '']
    # criadores
    b = [sec('criadores'), '']
    for city, cs in creators_by_city(d, lang):
        b += [f'### {city} ({len(cs)})', ''] + [creator_line(c, lang) for c in cs] + ['']
    b += [f"{d['join'][0]} {d['join'][1]}", '', d['notice']]
    out += b + ['']
    # agências
    out += [sec('agencias'), '']
    for a in sorted(d['agencies'], key=lambda a: a['name'].lower()):
        bd = badge(a['b'], lang)
        out.append(f"- [{a['name']}]({ig(a['handle'])}) @{a['handle']}" + (f': {bd}' if bd else ''))
    out.append('')
    # apps e perfis
    out += [sec('apps'), '', f"### {w['apps']}", '']
    for cat, items in d['apps']:
        out += [f'#### {cat}', ''] + [f'- [{n}]({u}): {desc}' for n, desc, u in items] + ['']
    out += [f"### {w['profiles']}", '']
    for cat, items in d['profiles']:
        out += [f'#### {cat}', ''] + [f'- [{n}]({ig(h)}) @{h}' for n, h in items] + ['']
    # fatos
    f = d['facts']; L2 = (lambda p, e: p) if lang == 'pt' else (lambda p, e: e)
    out += [sec('fatos'), '', f"### {w['stats']}", ''] + [f'- **{L2(vp, ve)}** {L2(lp, le)}' for vp, ve, lp, le in f['stats']] + ['']
    out += [f'### {L2(tp, te)}\n\n{L2(dp, de)}\n' for tp, te, dp, de in f['facts']]
    fmt = (lambda n: f'{n:,}'.replace(',', '.')) if lang == 'pt' else (lambda n: f'{n:,}')
    out += [f"### {w['popcities']}", ''] + [f'{rk}. {L2(np_, ne)} ({st}): {fmt(pop)}' for rk, np_, ne, pop, st in f['cities']]
    out += [''] + [n for n in s['fatos']['notes']] + [srcs('fatos').strip(), '']
    # cidades
    out += [sec('cidades'), '']
    for c in d['cities']:
        out += [f"### {c['n']} ({c['c']} · {c['st']})", '',
                f"- {w['rent']}: A$ {c['rent']}", f"- {w['pop']}: {c['pop']}", f"- {w['max']}: {c['sum']} · {c['win']}",
                f"- {w['visa']}: {c['reg']}", f"- {w['jobs']}: {c['s']['emprego']}/5 · {w['br']}: {c['s']['br']}/5",
                f"- {w['pro']}: {c['pro']}", f"- {w['con']}: {c['con']}", f"- {w['good']}: {c['bom']}", '']
    out += s['cidades']['notes'] + [srcs('cidades').strip(), '']
    # guia
    out += [sec('guia'), '']
    for i, g in enumerate(d['guide'], 1):
        out += [f"### {i}. {g['t']}", '', f"_{g['s']}_", '', g['body'], '']
    # perguntas frequentes
    out += [f"## {d['faqh']}", '', d['faqp'], '', f"Link: {anchor(lang, 'faq')}", '']
    for q, a in d['faq']:
        out += [f'### {q}', '', a, '']
    # dicionário
    out += [sec('dicionario'), '']
    out += [f'- **{t}**: {pt} ({en})' if lang == 'pt' else f'- **{t}**: {en}' for t, en, pt in d['dict']] + ['']
    # vídeos
    out += [sec('reels'), ''] + [f'- [{t}]({u})' for t, u in d['reels']] + ['']
    # sobre
    a = d['about']
    out += [f"## {d['tabs'].get('sobre', 'Sobre')}", '', f"{a['label']}: {a['name']}. {a['role']}", ''] + [p + '\n' for p in a['body']]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'


def index_md():
    p, e, s = P, E, P['sec']
    n = {'criadores': len(p['creators']), 'agencias': len(p['agencies']), 'apps': sum(len(i) for _, i in p['apps']),
         'perfis': sum(len(i) for _, i in p['profiles']), 'dicionario': len(p['dict']), 'cidades': len(p['cities']),
         'guia': len(p['guide']), 'reels': len(p['reels'])}
    cnt = {'criadores': f"{n['criadores']} criadores", 'agencias': f"{n['agencias']} agências",
           'apps': f"{n['apps']} apps e serviços, {n['perfis']} perfis", 'cidades': f"{n['cidades']} cidades comparadas",
           'guia': f"{n['guia']} etapas", 'dicionario': f"{n['dicionario']} termos", 'reels': f"{n['reels']} vídeos", 'fatos': '', 'sobre': ''}
    o = [f'# Brasileiros na Austrália', '', f"> {p['lede']}", '',
         'Diretório gratuito e bilíngue (português do Brasil e inglês australiano) para brasileiros que vivem ou querem viver na Austrália, '
         'parte da BiblioVerse. É uma página única com abas: o português fica na raiz e o inglês em ?lang=en. '
         'As listas são montadas por JavaScript, por isso o conteúdo completo também está publicado em Markdown abaixo. '
         f"Atualizado em {TODAY}. {p['footer'][1] if len(p['footer']) > 1 else ''}", '',
         '## Conteúdo completo', '',
         f'- [Conteúdo completo em português]({BASE}llms-full.txt): todos os criadores por cidade, agências, apps, perfis, fatos, cidades, guia de chegada, dicionário e vídeos',
         f'- [Full content in English]({BASE}llms-full-en.txt): the same content in English', '',
         '## Seções', '']
    for k in TAB_ORDER:
        if k == 'sobre' or k not in s: continue
        o.append(f"- [{s[k]['h']}]({anchor('pt', k)}): {s[k]['p']}" + (f' ({cnt[k]})' if cnt[k] else ''))
    o += ['', f"## {p['faqh']}", '', f"{p['faqp']} Link: {anchor('pt', 'faq')}", ''] + [f'- **{q}** {a}' for q, a in p['faq']]
    o += ['', '## In English', '', f"- [Brazilians in Australia]({W['en']['url']}): {e['lede']}"]
    for k in TAB_ORDER:
        if k == 'sobre' or k not in e['sec']: continue
        o.append(f"- [{e['sec'][k]['h']}]({anchor('en', k)}): {e['sec'][k]['p']}")
    o += ['', '## Optional', '',
          '- [Cultura Australiana](https://australianculture.biblioverse.org/llms.txt): guia da cultura australiana, da mesma família de projetos',
          '- [Cultura Brasileira](https://brazilianculture.biblioverse.org/llms.txt): guia da cultura brasileira',
          '- [BiblioVerse](https://biblioverse.org/llms.txt): a biblioteca de bibliotecas da qual este site faz parte']
    return '\n'.join(o) + '\n'


def write(name, text):
    open(os.path.join(ROOT, name), 'w', encoding='utf-8', newline='\n').write(text)
    print(f'{name}: {len(text.encode("utf-8")):,} bytes')


write('llms.txt', index_md())
write('llms-full.txt', full(P, 'pt'))
write('llms-full-en.txt', full(E, 'en'))

# ------------------------------------------------------------------ JSON-LD
p, s = P, P['sec']
ID = lambda k: BASE + '#' + k
website = {'@type': 'WebSite', '@id': ID('website'), 'name': 'Brasileiros na Austrália', 'alternateName': 'Brazilians in Australia',
           'url': BASE, 'inLanguage': ['pt-BR', 'en-AU'],
           'description': 'Diretório para brasileiros na Austrália: criadores de conteúdo por cidade, comparador das capitais com aluguel, agências de intercâmbio, apps essenciais e guia de chegada passo a passo.',
           'author': {'@type': 'Person', 'name': 'Julio Cesar Prava', 'url': 'https://www.instagram.com/gdayjulio/',
                      'sameAs': ['https://www.instagram.com/gdayjulio/', 'https://www.tiktok.com/@gdayjulio',
                                 'https://www.linkedin.com/in/juliocesarprava', 'https://www.behance.net/juliocesarprava']},
           'publisher': {'@type': 'Organization', 'name': 'BiblioVerse', 'url': 'https://biblioverse.org/'}}
lists = []
lists.append({'@type': 'ItemList', '@id': ID('criadores'), 'name': s['criadores']['h'], 'description': s['criadores']['p'],
              'numberOfItems': len(p['creators']),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': c['name'], 'url': ig(c['handle']),
                                   'description': ' · '.join(x for x in [c['cityL'] or W['pt']['nocity'], ', '.join(c['typesL']),
                                                                         W['pt']['aussie'] if c['au'] else ''] if x)}
                                  for i, c in enumerate(p['creators'], 1)]})
lists.append({'@type': 'ItemList', '@id': ID('agencias'), 'name': s['agencias']['h'], 'description': s['agencias']['p'],
              'numberOfItems': len(p['agencies']),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'item': {'@type': 'Organization', 'name': a['name'], 'sameAs': ig(a['handle']),
                                   **({'description': badge(a['b'], 'pt').capitalize()} if a['b'] else {})}}
                                  for i, a in enumerate(sorted(p['agencies'], key=lambda a: a['name'].lower()), 1)]})
apps = [(cat, n, d, u) for cat, items in p['apps'] for n, d, u in items]
lists.append({'@type': 'ItemList', '@id': ID('apps'), 'name': W['pt']['apps'], 'description': s['apps']['p'], 'numberOfItems': len(apps),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n, 'url': u, 'description': f'{cat}: {d}'}
                                  for i, (cat, n, d, u) in enumerate(apps, 1)]})
profs = [(cat, n, h) for cat, items in p['profiles'] for n, h in items]
lists.append({'@type': 'ItemList', '@id': ID('perfis'), 'name': W['pt']['profiles'], 'numberOfItems': len(profs),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n, 'url': ig(h), 'description': cat}
                                  for i, (cat, n, h) in enumerate(profs, 1)]})
lists.append({'@type': 'ItemList', '@id': ID('cidades'), 'name': s['cidades']['h'], 'description': s['cidades']['p'], 'numberOfItems': len(p['cities']),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'item': {'@type': 'City', 'name': c['n'],
                                   'containedInPlace': {'@type': 'State', 'name': c['st']},
                                   'description': f"{c['pro']} {W['pt']['con']}: {c['con']} {W['pt']['rent']}: A$ {c['rent']}."}}
                                  for i, c in enumerate(p['cities'], 1)]})
lists.append({'@type': 'HowTo', '@id': ID('guia'), 'name': s['guia']['h'], 'description': s['guia']['p'], 'inLanguage': 'pt-BR',
              'step': [{'@type': 'HowToStep', 'position': i, 'name': g['t'], 'text': g['s'],
                        'itemListElement': [{'@type': 'HowToDirection', 'text': h} for h in g['h']]}
                       for i, g in enumerate(p['guide'], 1)]})
lists.append({'@type': 'FAQPage', '@id': ID('faq'), 'name': p['faqh'], 'description': p['faqp'], 'inLanguage': 'pt-BR',
              'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]})
lists.append({'@type': 'DefinedTermSet', '@id': ID('dicionario'), 'name': s['dicionario']['h'], 'description': s['dicionario']['p'],
              'hasDefinedTerm': [{'@type': 'DefinedTerm', 'name': t, 'description': f'{pt} ({en})'} for t, en, pt in p['dict']]})
lists.append({'@type': 'ItemList', '@id': ID('reels'), 'name': s['reels']['h'], 'numberOfItems': len(p['reels']),
              'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': t, 'url': u} for i, (t, u) in enumerate(p['reels'], 1)]})
webpage = {'@type': 'WebPage', '@id': ID('webpage'), 'url': BASE, 'name': p['title'], 'description': website['description'],
           'inLanguage': 'pt-BR', 'isPartOf': {'@id': ID('website')}, 'datePublished': PUBLISHED, 'dateModified': TODAY,
           'author': website['author'], 'publisher': website['publisher'],
           'about': [{'@type': 'Country', 'name': 'Austrália', 'sameAs': 'https://www.wikidata.org/wiki/Q408'},
                     {'@type': 'Thing', 'name': 'Imigração brasileira na Austrália'}],
           'audience': {'@type': 'Audience', 'audienceType': 'Brasileiros que vivem ou querem viver na Austrália'},
           'image': BASE + 'og-image.png', 'hasPart': [{'@id': x['@id']} for x in lists]}
ld = json.dumps({'@context': 'https://schema.org', '@graph': [website, webpage] + lists}, ensure_ascii=False, separators=(',', ':'))
ld = ld.replace('</', '<\\/')
block = ('<!-- seo:start -->\n<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">\n'
         f'<script type="application/ld+json">{ld}</script>\n<!-- seo:end -->')

raw = open(INDEX, 'rb').read().decode('utf-8')
nl = '\r\n' if '\r\n' in raw else '\n'
src = raw.replace('\r\n', '\n')
d_ = datetime.date.today()
upd_pt = f'<span data-i18n="kupd">Atualizado em <time datetime="{TODAY}">{d_.day} de {MESES[d_.month - 1]} de {d_.year}</time></span>'
upd_en = f'Updated <time datetime=\\"{TODAY}\\">{d_.day} {MONTHS[d_.month - 1]} {d_.year}</time>'
src = re.sub(r'<!-- upd:start -->.*?<!-- upd:end -->', lambda m: f'<!-- upd:start -->{upd_pt}<!-- upd:end -->', src, flags=re.S)
src = re.sub(r'"kupd": "(?:[^"\\]|\\.)*"', lambda m: f'"kupd": "{upd_en}"', src)  # aceita \" dentro do valor
if '<!-- seo:start -->' in src:
    src = re.sub(r'<!-- seo:start -->.*?<!-- seo:end -->', lambda m: block, src, flags=re.S)
else:
    old = re.search(r'<script type="application/ld\+json">.*?</script>', src, re.S)
    src = src[:old.start()] + block + src[old.end():]
open(INDEX, 'w', encoding='utf-8', newline='').write(src.replace('\n', nl))
print(f'JSON-LD: {len(ld.encode("utf-8")):,} bytes, {len(lists)} listas')

sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
write('sitemap.xml', re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', sm))
rb = open(os.path.join(ROOT, 'robots.txt'), encoding='utf-8').read()
if 'llms.txt' not in rb:
    write('robots.txt', rb.rstrip('\n') + f'\n# Resumo para modelos de linguagem: {BASE}llms.txt\n')
