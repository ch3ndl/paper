"""Check generated local links, fragments, and image references before publication."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]/'_site'
class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a and not urlsplit(a[key]).scheme:self.links.append(a[key])
pages={p:Links() for p in ROOT.rglob('*.html')}
for p,parser in pages.items():parser.feed(p.read_text(encoding='utf-8'))
errors=[]
for p,parser in pages.items():
    for value in parser.links:
        u=urlsplit(value)
        if not value or value=='#':continue
        dest=(p.parent/unquote(u.path)).resolve() if u.path else p
        if dest.is_dir():dest=dest/'index.html'
        if not dest.is_file():errors.append(f'{p.name}: missing {value}')
        elif u.fragment and dest in pages and unquote(u.fragment) not in pages[dest].ids:errors.append(f'{p.name}: missing fragment {value}')
if errors:raise SystemExit('\n'.join(errors))
print('Verified local links and fragments across',len(pages),'pages')
