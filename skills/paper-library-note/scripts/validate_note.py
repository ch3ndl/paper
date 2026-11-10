"""Validate the bilingual annotation format, shared by export and website build."""
import datetime, re
from pathlib import Path
from urllib.parse import urlsplit
KINDS={'thesis','term','evidence','concession','method'}
def validate(n, root=None):
    if n.get('schemaVersion')!=2: raise ValueError('双语批注文件需要 schemaVersion 2')
    for k in ('slug','title','summary','category','coverage','course'):
        if not isinstance(n.get(k),str) or not n[k].strip(): raise ValueError('缺少 '+k)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',n['slug']): raise ValueError('slug 格式错误')
    if not isinstance(n.get('year'),int) or not 1000<=n['year']<=9999:raise ValueError('year 格式错误')
    datetime.date.fromisoformat(n['updated'])
    if n.get('status') not in ('draft','reviewed','imported'):raise ValueError('status 格式错误')
    if not isinstance(n.get('tags'),list) or not all(isinstance(t,str) and t.strip() for t in n['tags']):raise ValueError('tags 格式错误')
    for k in ('url','citation','license'):
        if not n.get('source',{}).get(k):raise ValueError('source 缺少 '+k)
    if urlsplit(n['source']['url']).scheme not in ('http','https'):raise ValueError('原文链接必须为 http(s)')
    if not n.get('sections'):raise ValueError('缺少原文章节')
    ids=set()
    for s in n['sections']:
        for k in ('id','title','originalHeading','sourceLocation'):
            if not isinstance(s.get(k),str) or not s[k].strip():raise ValueError('章节缺少 '+k)
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',s['id']) or s['id'] in ids:raise ValueError('章节 id 错误或重复')
        ids.add(s['id'])
        if not s.get('blocks'):raise ValueError('章节没有段落')
        for b in s['blocks']:
            for k in ('heading','english','translation','explanation','sourceLocation'):
                if not isinstance(b.get(k),str) or not b[k].strip():raise ValueError('段落缺少 '+k)
            for k in ('function','role','critique'):
                if not isinstance(b.get('annotation',{}).get(k),str) or not b['annotation'][k].strip():raise ValueError('批注缺少 '+k)
            ranges=[]
            for h in b.get('highlights',[]):
                if h.get('kind') not in KINDS or not h.get('text'):raise ValueError('高亮维度或内容无效')
                start=b['english'].find(h['text'])
                if start<0:raise ValueError('高亮文字不在英文原文中：'+h['text'])
                stop=start+len(h['text'])
                if any(start<e and stop>a for a,e in ranges):raise ValueError('高亮片段重叠')
                ranges.append((start,stop))
            for f in b.get('figures',[]):
                if not re.fullmatch('assets/images/'+re.escape(n['slug'])+r'/[A-Za-z0-9_-]+\.(png|jpe?g|webp)',f.get('path','')):raise ValueError('图片路径无效')
                for k in ('alt','caption','source','license'):
                    if not f.get(k):raise ValueError('图片缺少 '+k)
                if urlsplit(f['source']).scheme not in ('http','https'):raise ValueError('图片来源链接无效')
                if root is not None and not (Path(root)/f['path']).is_file():raise ValueError('缺少图片 '+f['path'])
            for t in b.get('tables',[]):
                if not t.get('caption') or not t.get('headers') or not t.get('rows'):raise ValueError('表格缺少标题/表头/数据')
                if any(len(row)!=len(t['headers']) for row in t['rows']):raise ValueError('表格列数不一致')
    amap=n.get('argumentMap',{})
    for k in ('problem','thesis','evidence','rebuttal','conclusion','claim','strongest','weakest'):
        if not isinstance(amap.get(k),str) or not amap[k].strip():raise ValueError('论证总览缺少 '+k)
    return n
