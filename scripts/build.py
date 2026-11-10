"""Build the paper library, using only Python's standard library."""
import html, json, re, shutil
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
def esc(s): return html.escape(str(s), quote=True)
def paras(s): return ''.join('<p>'+esc(p).replace('\n','<br>')+'</p>' for p in s.split('\n\n') if p.strip())
def url(s):
    if urlsplit(s).scheme not in ('https', 'http'): raise ValueError('来源链接必须是 http(s) URL')
    return esc(s)
def validate(n, root=ROOT):
    if n.get('schemaVersion') != 1: raise ValueError('仅支持 schemaVersion 1')
    for k in ('slug','title','summary','category','year','updated','source','coverage','sections','tags'):
        if k not in n: raise ValueError('缺少字段 '+k)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',n['slug']): raise ValueError('slug 格式错误')
    for k in ('title','summary','category','coverage'):
        if not isinstance(n[k],str) or not n[k].strip(): raise ValueError(k+' 不能为空')
    if not isinstance(n['year'],int) or not 1000<=n['year']<=9999: raise ValueError('year 必须为四位年份')
    import datetime
    datetime.date.fromisoformat(n['updated'])
    if not isinstance(n['tags'],list) or not all(isinstance(t,str) and t.strip() for t in n['tags']): raise ValueError('tags 必须是文本数组')
    if not isinstance(n['source'],dict): raise ValueError('source 必须是对象')
    url(n['source']['url'])
    if not n['source'].get('citation'): raise ValueError('缺少 citation')
    if n.get('status','draft') not in ('draft','reviewed','imported'): raise ValueError('未知核对状态')
    if not n['sections']: raise ValueError('至少需要一个原文章节')
    ids=set()
    for s in n['sections']:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',s['id']) or s['id'] in ids: raise ValueError('章节 id 无效或重复')
        ids.add(s['id'])
        for k in ('title','originalHeading','sourceLocation'):
            if not isinstance(s.get(k),str) or not s[k].strip(): raise ValueError('章节缺少 '+k)
        if not s.get('blocks'): raise ValueError('章节内容不能为空')
        for b in s['blocks']:
            for k in ('heading','explanation'):
                if not isinstance(b.get(k),str) or not b[k].strip(): raise ValueError('内容缺少 '+k)
            for k in ('analysis','englishParaphrase','quote'):
                if k in b and not isinstance(b[k],str): raise ValueError(k+' 必须为文本')
            for f in b.get('figures',[]):
                p=f['path']
                if not re.fullmatch(r'assets/images/'+re.escape(n['slug'])+r'/[A-Za-z0-9_-]+\.(?:png|jpe?g|webp)',p): raise ValueError('图片路径必须在 assets/images/<slug>/，且为 PNG/JPEG/WebP')
                if not (root/p).is_file(): raise ValueError('图片不存在 '+p)
                for k in ('alt','caption','source','license'):
                    if not f.get(k): raise ValueError('图片缺少 '+k)
                url(f['source'])
    return n

def shell(title, body, prefix='./', active='', extra=''):
    nav=''.join(f'<a {"aria-current=page" if active==key else ""} href="{prefix}{target}">{label}</a>' for key,target,label in [('library','index.html','论文库'),('guide','guide.html','阅读与发布'),('admin','admin.html','管理')])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Saline 的论文精读与研究笔记"><title>{esc(title)} · Saline Papers</title><link rel="stylesheet" href="{prefix}assets/site.css"><script defer src="{prefix}assets/site.js"></script>{extra}</head><body><a class="skip" href="#main">跳到内容</a><header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-icon">S.</span><span>SALINE <b>PAPERS</b><small>论文与研究笔记</small></span></a><nav aria-label="站点导航">{nav}<a href="https://github.com/ch3ndl/paper" target="_blank" rel="noopener">GitHub ↗</a></nav></header>{body}<footer class="site-footer"><span>SALINE PAPERS <i> / </i> 让阅读留下线索。</span><span>AI 辅助整理 · 以原文证据为准 <a href="{prefix}guide.html">关于本站 ↗</a></span></footer><dialog id="image-dialog"><button type="button" id="close-image">关闭 ×</button><img alt=""><p></p></dialog></body></html>'''

def article(n):
    toc='<a href="#overview">阅读概览</a>'+''.join(f'<a href="#{esc(s["id"])}">{i:02d} {esc(s["title"])}</a>' for i,s in enumerate(n['sections'],1))+'<a href="#assessment">综合评议</a>'
    sections=''
    for i,s in enumerate(n['sections'],1):
        blocks=''
        for b in s['blocks']:
            optional=''
            if b.get('quote'): optional+='<blockquote><small>原文短摘录</small>'+paras(b['quote'])+'</blockquote>'
            if b.get('englishParaphrase'): optional+='<details><summary>English · AI 改写，非原文引句</summary>'+paras(b['englishParaphrase'])+'</details>'
            figures=''
            for f in b.get('figures',[]):
                figures+=f'<figure><button class="figure-zoom" type="button" aria-label="放大：{esc(f["alt"])}"><img loading="lazy" src="../{esc(f["path"])}" alt="{esc(f["alt"])}"></button><figcaption>{paras(f["caption"])}<a href="{url(f["source"])}" target="_blank" rel="noopener">图片来源 ↗</a> · {esc(f["license"])}</figcaption></figure>'
            analysis=paras(b.get('analysis','该段暂无独立评议。'))
            blocks+=f'<div class="reading-pair"><div class="explanation"><h3>{esc(b["heading"])}</h3>{paras(b["explanation"])}{optional}{figures}</div><aside class="annotation"><span class="eyebrow">阅读批注 · AI 分析</span>{analysis}</aside></div>'
        sections+=f'<section class="paper-section" id="{esc(s["id"])}"><div class="section-title"><span>{i:02d}</span><div><h2>{esc(s["title"])}</h2><p>{esc(s["originalHeading"])} · {esc(s["sourceLocation"])}</p></div></div>{blocks}</section>'
    status={'draft':'待核对','reviewed':'已人工核对','imported':'附件迁移 · 待核对'}[n.get('status','draft')]
    body=f'''<div class="reading-progress" aria-hidden="true"></div><main id="main"><section class="paper-hero"><div class="eyebrow">{esc(n['category'])} / {n['year']} / {status}</div><h1>{esc(n['title'])}</h1><p class="paper-subtitle">{esc(n.get('subtitle',''))}</p><p class="citation">{esc(n['source']['citation'])}</p><div class="hero-links"><a href="{url(n['source']['url'])}" target="_blank" rel="noopener">阅读原文 ↗</a><a href="../notes/{esc(n['slug'])}.json" download>下载笔记 JSON ↓</a><button id="bookmark" type="button">收藏到本机</button><button type="button" onclick="window.print()">打印 / PDF</button></div></section><div class="reader-layout"><aside class="toc"><span class="eyebrow">CONTENTS / 目录</span><nav aria-label="论文目录">{toc}</nav><div class="reader-controls"><label for="reading-mode">阅读布局</label><select id="reading-mode"><option value="annotated">正文 + 批注</option><option value="focus">专注正文</option></select><label for="font-size">文字大小</label><input id="font-size" type="range" min="15" max="23" value="17"><a id="resume" hidden href="#">继续上次阅读 →</a></div></aside><article class="paper-body"><section id="overview"><div class="notice">阅读范围：{esc(n['coverage'])}</div><span class="eyebrow">THE IDEA / 一句话</span><p class="lead">{esc(n['summary'])}</p><div class="tag-list">{''.join('<span>'+esc(t)+'</span>' for t in n['tags'])}</div></section>{sections}<section id="assessment" class="assessment"><span class="eyebrow">AFTER READING / 读后整理</span><h2>贡献、边界与下一步</h2>{paras(n.get('assessment','尚未添加综合评议。'))}</section><p class="end-note">更新于 {esc(n['updated'])} · 此页为 AI 辅助阅读笔记，数据与论断请结合原文核查。</p></article></div></main>'''
    return shell(n['title'],body,'../','library')

def build():
    notes=[]
    for p in sorted((ROOT/'notes').glob('*.json')):
        n=validate(json.loads(p.read_text(encoding='utf-8')))
        if p.stem!=n['slug']: raise ValueError('文件名必须与 slug 一致：'+p.name)
        notes.append(n)
    if OUT.exists():
        if OUT.resolve().parent != ROOT.resolve() or OUT.name != '_site': raise ValueError('Invalid output directory')
        shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)
    for folder in ('assets','notes','skills'):
        if (ROOT/folder).exists(): shutil.copytree(ROOT/folder,OUT/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (OUT/'templates').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'templates/note.example.json',OUT/'templates/note.example.json')
    (OUT/'papers').mkdir(exist_ok=True)
    for n in notes: (OUT/'papers'/f'{n["slug"]}.html').write_text(article(n),encoding='utf-8')
    cards=''
    for n in sorted(notes,key=lambda x:x['updated'],reverse=True):
        tags=''.join('<span>'+esc(t)+'</span>' for t in n['tags'])
        cards+=f'''<article class="paper-card" data-title="{esc(n['title']+' '+n.get('subtitle','')+' '+n['summary']+' '+' '.join(n['tags']))}" data-category="{esc(n['category'])}" data-tags="{esc(json.dumps(n['tags'],ensure_ascii=False))}" data-year="{n['year']}" data-updated="{esc(n['updated'])}" data-slug="{esc(n['slug'])}"><div class="card-top"><span>{esc(n['category'])}</span><span>{n['year']} · {'待核对' if n.get('status')!='reviewed' else '已核对'}</span></div><h2><a href="papers/{esc(n['slug'])}.html">{esc(n['title'])} <span>↗</span></a></h2><p>{esc(n['summary'])}</p><div class="tag-list">{tags}</div><div class="card-bottom"><span>{len(n['sections'])} 个章节 · {esc(n['updated'])}</span><button class="card-bookmark" type="button" data-slug="{esc(n['slug'])}" aria-label="收藏 {esc(n['title'])}">☆</button></div></article>'''
    cats=sorted(set(n['category'] for n in notes)); tags=sorted(set(t for n in notes for t in n['tags']))
    filters=''.join(f'<option>{esc(c)}</option>' for c in cats)
    tagfilters=''.join(f'<button type="button" class="tag-filter" aria-pressed="false" data-tag="{esc(t)}">{esc(t)}</button>' for t in tags)
    body=f'''<main id="main" class="library"><section class="library-hero"><div><div class="eyebrow">A PERSONAL RESEARCH LIBRARY</div><h1>把论文读进去，<br><em>把思考留下来。</em></h1><p>沿着原文的结构理解研究，<br>把方法、证据与自己的判断放回各自的位置。</p><a class="text-link" href="guide.html">了解笔记的阅读方式 <span>↗</span></a></div><aside class="hero-note"><span class="eyebrow">THE READING METHOD</span><div><b>01</b><p>顺着原文读<small>保留章节顺序与证据位置</small></p></div><div><b>02</b><p>对着图表想<small>从研究设计走到具体发现</small></p></div><div><b>03</b><p>带着问题走<small>分清作者结论与阅读批注</small></p></div></aside></section><section class="library-section"><div class="library-title"><h2>论文书架 <span>{len(notes):02d}</span></h2><a href="admin.html">整理新笔记 +</a></div><div class="filters"><label class="search-label"><span class="sr-only">搜索论文</span><input type="search" id="search" placeholder="搜索标题、关键词或研究问题…"></label><label><span class="sr-only">分类</span><select id="category"><option value="">全部分类</option>{filters}</select></label><label><span class="sr-only">排序</span><select id="sort"><option value="updated">最近更新</option><option value="year">发表年份</option><option value="title">标题排序</option></select></label><label class="saved-filter"><input type="checkbox" id="saved-only"> 本机收藏</label></div><div class="tag-filters"><button class="tag-filter active" id="all-tags" type="button" aria-pressed="true">全部标签</button>{tagfilters}</div><p class="result-count" aria-live="polite"></p><div class="paper-grid">{cards}</div><div id="empty" class="empty" hidden>没有找到符合条件的论文。<button id="reset" type="button">清除筛选</button></div></section></main>'''
    (OUT/'index.html').write_text(shell('论文库',body,active='library'),encoding='utf-8')
    for name in ('guide','admin'):
        body=(ROOT/'templates'/f'{name}.html').read_text(encoding='utf-8')
        extra='<script defer src="assets/admin.js"></script>' if name=='admin' else ''
        (OUT/f'{name}.html').write_text(shell('管理论文' if name=='admin' else '阅读与发布',body,active=name,extra=extra),encoding='utf-8')
    catalog=[{k:n[k] for k in ('slug','title','category','tags','year','updated')} for n in notes]
    (OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf-8')
    (OUT/'.nojekyll').touch()
    (OUT/'404.html').write_text(shell('页面未找到','<main id="main" class="prose"><h1>这篇笔记还不在书架上。</h1><a href="https://ch3ndl.github.io/paper/">返回论文库 →</a></main>'),encoding='utf-8')
    print(f'Built {len(notes)} notes into {OUT}')

if __name__=='__main__': build()
