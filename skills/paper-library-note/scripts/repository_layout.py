"""One paper directory = result.zip, README.md and authoritative taxonomy.txt."""
import json,re,zipfile
from pathlib import Path, PurePosixPath
from validate_note import validate

def category_path(value):
    if not isinstance(value,str) or '\n' in value or value.strip().startswith(('[','{')):raise ValueError('分类必须是一条文本路径')
    segments=[s.strip() for s in value.split('/')]
    if not segments or any(not s for s in segments):raise ValueError('分类层级不能为空，请使用 父分类 / 子分类')
    return ' / '.join(segments)

def read_taxonomy(text):
    category=None;tags=[];in_tags=False;seen_tags=False
    for line in text.lstrip('\ufeff').splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        if in_tags and line.startswith('- '):
            tag=line[2:].strip()
            if not tag:raise ValueError('标签不能为空')
            if tag not in tags:tags.append(tag)
            continue
        match=re.fullmatch(r'(分类|category|标签|tags)\s*[:：]\s*(.*)',line)
        if not match:raise ValueError('taxonomy.txt 不认识这一行：'+line)
        key,value=match.groups()
        if key in ('分类','category'):
            if category is not None:raise ValueError('每篇文章只能有一个分类，不可重复填写分类行')
            category=category_path(value);in_tags=False
        else:
            if seen_tags:raise ValueError('标签栏目只能出现一次')
            seen_tags=True;in_tags=True
            if value:
                for tag in re.split('[,，]',value):
                    tag=tag.strip()
                    if not tag:raise ValueError('标签不能为空')
                    if tag not in tags:tags.append(tag)
    if category is None:raise ValueError('taxonomy.txt 缺少分类')
    if not seen_tags:raise ValueError('taxonomy.txt 缺少标签栏目，无标签时保留空的 标签:')
    return category,tags

def taxonomy_text(category,tags):
    category=category_path(category)
    if not isinstance(tags,list) or any(not isinstance(t,str) or not t.strip() or '\n' in t for t in tags):raise ValueError('标签必须为单行文本数组')
    return '# 每篇论文只有一条分类路径；/ 表示下一级。标签可以有多个。\n分类: '+category+'\n\n标签:\n'+''.join('- '+t.strip()+'\n' for t in dict.fromkeys(t.strip()for t in tags))

def write_submission(note,archive,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    # Preserve an already edited taxonomy file when refreshing the result package.
    taxonomy=directory/'taxonomy.txt'
    if not taxonomy.exists():taxonomy.write_text(taxonomy_text(note['category'],note['tags']),encoding='utf-8')
    read_taxonomy(taxonomy.read_text(encoding='utf-8-sig'))
    authors=note.get('authors')
    author_text='；'.join(authors) if isinstance(authors,list) and authors else '未单独填写，详见下方文献出处。'
    text=f'''# {note['title']}

{note.get('subtitle','')}

- **作者**：{author_text}
- **发表年份**：{note['year']}
- **原文链接**：{note['source']['url']}
- **文献出处**：{note['source']['citation']}
- **最后整理**：{note['updated']}

## 简介

{note['summary']}

## 阅读范围

{note['coverage']}

## 文件

- [result.zip](result.zip)：双语批注 HTML、结构化笔记与图片的完整结果包。
- [taxonomy.txt](taxonomy.txt)：分类和标签的唯一管理文件，可直接在 GitHub 编辑。

修改分类或标签后提交即可更新网站。替换 result.zip 可更新笔记内容；删除整个论文目录可从网站下架。论文目录名保持 `{note['slug']}`，以保持已发布链接稳定。
'''
    if not (directory/'README.md').exists():(directory/'README.md').write_text(text,encoding='utf-8')
    return directory

def load_submission(directory,staging):
    directory=Path(directory);staging=Path(staging);slug=directory.name
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('论文目录名只能使用小写英文、数字和连字符：'+slug)
    for filename in ('result.zip','README.md','taxonomy.txt'):
        if not (directory/filename).is_file():raise ValueError(slug+' 缺少 '+filename)
    if not (directory/'README.md').read_text(encoding='utf-8-sig').strip():raise ValueError(slug+' README.md 不能为空')
    category,tags=read_taxonomy((directory/'taxonomy.txt').read_text(encoding='utf-8-sig'))
    archive=directory/'result.zip'
    if archive.stat().st_size>30*1024*1024:raise ValueError(slug+' 的结果包大于30MiB')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist();names=[i.filename for i in infos]
        if len(infos)>100 or len(set(names))!=len(names):raise ValueError('结果包文件过多或含重复路径')
        if sum(i.file_size for i in infos)>30*1024*1024 or any(i.file_size>12*1024*1024 for i in infos):raise ValueError('结果包解压后过大')
        for info in infos:
            p=PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in info.filename or ':' in info.filename:raise ValueError('不安全的结果包路径')
            if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('结果包不能包含符号链接')
        note_path='notes/'+slug+'.json'
        if [p for p in names if p.startswith('notes/') and p.endswith('.json')]!=[note_path]:raise ValueError('结果包必须且仅包含 notes/'+slug+'.json')
        n=json.loads(z.read(note_path).decode('utf-8-sig'))
        if n.get('slug')!=slug:raise ValueError('目录名与结果包中的论文标识不一致')
        n['category']=category;n['tags']=tags
        for s in n.get('sections',[]):
            for b in s.get('blocks',[]):
                for f in b.get('figures',[]):
                    path=f.get('path','')
                    if not re.fullmatch('assets/images/'+re.escape(slug)+r'/[A-Za-z0-9_-]+\.(png|jpe?g|webp)',path):raise ValueError('图片路径不属于当前论文')
                    data=z.read(path)
                    if not(data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff') or (data.startswith(b'RIFF')and data[8:12]==b'WEBP')):raise ValueError('图片内容无效：'+path)
                    target=staging/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        validate(n,staging)
    return n

def load_library(library,staging):
    library=Path(library);notes=[]
    if not library.exists():return notes
    for directory in sorted(library.iterdir()):
        if directory.is_dir() and not directory.name.startswith('.'):
            try:notes.append(load_submission(directory,staging))
            except (ValueError,KeyError,zipfile.BadZipFile,json.JSONDecodeError) as error:raise ValueError(directory.name+': '+str(error)) from error
    return notes
