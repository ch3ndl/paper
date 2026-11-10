"""One-time migration of the user-supplied reference. Does not execute its HTML."""
import re, html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def plain(s): return html.unescape(re.sub('<[^>]+>','',s)).strip()
def migrate(source):
    raw=Path(source).read_text(encoding='utf-8')
    sections=[]
    for match in re.finditer(r'<section id="([^"]+)">(.*?)</section>',raw,re.S):
        sid,chunk=match.groups()
        if sid=='argument-map': continue
        heading=plain(re.search(r'<h2>(.*?)</h2>',chunk,re.S).group(1))
        blocks=[]
        for pair in re.finditer(r'<article class="pair"[^>]*>(.*?)</article>',chunk,re.S):
            c=pair.group(1)
            title=re.search(r'<h3 class="passage-title">(.*?)</h3>',c,re.S)
            en=re.search(r'<p class="english">(.*?)</p>',c,re.S)
            zh=re.search(r'<div class="translation"><span[^>]*>.*?</span>(.*?)</div>',c,re.S)
            if not(title and en and zh): continue
            an=re.search(r'<aside class="annotation"[^>]*>(.*?)</aside>',c,re.S)
            analysis='\n\n'.join(plain(p) for p in re.findall(r'<p>(.*?)</p>',an.group(1),re.S)) if an else ''
            blocks.append(dict(heading=plain(title.group(1)),explanation=plain(zh.group(1)),englishParaphrase=plain(en.group(1)),analysis=analysis))
        if blocks: sections.append(dict(id=sid,title=heading.split('｜')[-1],originalHeading=heading,sourceLocation='附件中的 '+heading+'；原文具体段落位置待复核',blocks=blocks))
    n=dict(schemaVersion=1,slug='deeploc-2',title='DeepLoc 2.0：从蛋白质序列到多标签亚细胞定位',subtitle='Multi-label subcellular localization prediction using protein language models',year=2022,category='蛋白质定位',tags=['蛋白语言模型','亚细胞定位','多标签分类'],updated='2026-11-11',status='imported',source=dict(url='https://doi.org/10.1093/nar/gkac278',citation='Thumuluri V, Almagro Armenteros JJ, Johansen AR, Nielsen H, Winther O. Nucleic Acids Research, 2022, 50(W1): W228–W234. DOI: 10.1093/nar/gkac278.'),summary='DeepLoc 2.0 将预训练蛋白质语言模型与多标签预测结合，仅用序列预测多个亚细胞定位，并通过注意力和分选信号预测提供辅助解释线索。',coverage='本篇由用户提供的双语批注 HTML 迁移，保留其 19 个论证单元与 7 个章节；不是对原论文的完整重新精读。英文为旧笔记中的 AI 改写，不是原文引句。旧模板重排过章节，原文小节覆盖、表格数值和补充材料仍待逐项核对。',sections=sections,assessment='以下评议沿用附件，尚未独立核对：内部同源性控制与独立 HPA 测试提供不同层面的预测证据；总体指标优势不能外推为每个定位类别均占优。\n\n注意力与信号位置对齐可作为解释线索，不能直接等同于因果解释。需要继续核查长尾类别的表现、基准比较条件以及各模型组件的独立贡献。')
    assert sum(len(s['blocks']) for s in sections)==19,[(s['id'],len(s['blocks'])) for s in sections]
    (ROOT/'notes'/'deeploc-2.json').write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Migrated 19 reading blocks in',len(sections),'sections')
if __name__=='__main__':
    import sys
    migrate(sys.argv[1])
