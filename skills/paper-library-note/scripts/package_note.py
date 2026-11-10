"""Validate and export exactly one note with its referenced image assets."""
import datetime, json, re, sys, zipfile
from pathlib import Path
from urllib.parse import urlsplit

def check_url(u):
    if not isinstance(u,str) or urlsplit(u).scheme not in ('https','http') or not urlsplit(u).netloc: raise ValueError('Invalid source URL')

def package(root, slug, output):
    root=Path(root).resolve();output=Path(output).resolve()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Invalid slug')
    path=root/'notes'/f'{slug}.json';n=json.loads(path.read_text(encoding='utf-8'))
    if n.get('schemaVersion')==2:
        from validate_note import validate
        from render_note import render_html
        validate(n,root)
        html_path=root/'html'/f'{slug}.html';html_path.parent.mkdir(exist_ok=True)
        html_path.write_text(render_html(n,root),encoding='utf-8')
        files={path,html_path}
        for s in n['sections']:
            for b in s['blocks']:
                for f in b.get('figures',[]):
                    image=(root/f['path']).resolve();data=image.read_bytes()
                    if not(data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff') or (data.startswith(b'RIFF') and data[8:12]==b'WEBP')):raise ValueError('Invalid image bytes')
                    files.add(image)
        if len(files)>100 or any(p.stat().st_size>12*1024*1024 for p in files) or sum(p.stat().st_size for p in files)>29*1024*1024:raise ValueError('Export exceeds upload limit')
        output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as z:
            for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
        print(f'Validated bilingual note, standalone HTML and {len(files)-2} images: {output}')
        return output
    if n.get('schemaVersion')!=1 or n.get('slug')!=slug:raise ValueError('Schema version or slug mismatch')
    for k in ('title','summary','category','coverage'):
        if not isinstance(n.get(k),str) or not n[k].strip():raise ValueError('Missing '+k)
    if not isinstance(n.get('year'),int) or not 1000<=n['year']<=9999:raise ValueError('Invalid year')
    datetime.date.fromisoformat(n['updated'])
    if n.get('status') not in ('draft','reviewed','imported'):raise ValueError('Invalid review status')
    if not isinstance(n.get('tags'),list) or not all(isinstance(t,str) and t.strip() for t in n['tags']):raise ValueError('Invalid tags')
    check_url(n['source']['url'])
    if not n['source'].get('citation'):raise ValueError('Missing citation')
    if not n.get('sections'):raise ValueError('No sections')
    files={path};ids=set()
    for s in n['sections']:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',s['id']) or s['id'] in ids:raise ValueError('Invalid section id')
        ids.add(s['id'])
        for k in ('title','originalHeading','sourceLocation'):
            if not isinstance(s.get(k),str) or not s[k].strip():raise ValueError('Missing section '+k)
        if not s.get('blocks'):raise ValueError('Empty section')
        for b in s['blocks']:
            for k in ('heading','explanation'):
                if not isinstance(b.get(k),str) or not b[k].strip():raise ValueError('Missing block '+k)
            for k in ('analysis','englishParaphrase','quote'):
                if k in b and not isinstance(b[k],str):raise ValueError('Invalid text '+k)
            for f in b.get('figures',[]):
                if not re.fullmatch(r'assets/images/'+re.escape(slug)+r'/[A-Za-z0-9_-]+\.(png|jpe?g|webp)',f['path']):raise ValueError('Invalid image path')
                for k in ('alt','caption','source','license'):
                    if not f.get(k):raise ValueError('Missing image '+k)
                check_url(f['source']);p=(root/f['path']).resolve()
                if not p.is_relative_to(root) or not p.is_file():raise ValueError('Missing image '+f['path'])
                data=p.read_bytes()
                if not(data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff') or (data.startswith(b'RIFF') and data[8:12]==b'WEBP')):raise ValueError('Invalid image bytes '+f['path'])
                files.add(p)
    if len(files)>100 or any(p.stat().st_size>12*1024*1024 for p in files) or sum(p.stat().st_size for p in files)>29*1024*1024:raise ValueError('Export exceeds website upload limit')
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as z:
        for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
    print(f'Validated {len(n["sections"])} sections; packaged {len(files)} files: {output}')
    return output

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('Usage: package_note.py EXPORT_DIRECTORY SLUG OUTPUT.zip')
    package(*sys.argv[1:])
