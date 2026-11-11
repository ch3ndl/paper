"""Check original paragraph coverage and self-contained output, not merely field names."""
import copy, json, re, sys, tempfile, zipfile, xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/paper-library-note/scripts'))
from validate_note import validate
from render_note import render_html
from repository_layout import load_submission
clean=lambda el:re.sub(r'\s+',' ',''.join(el.itertext())).strip()
archive=ROOT/'library/deeploc-2/result.zip'
if not archive.exists():
    print('DeepLoc reference directory absent; no reference-specific check needed');raise SystemExit(0)
with zipfile.ZipFile(archive)as z:
    if 'sources/deeploc-2.xml' not in z.namelist():
        print('Original XML absent; generic build validation still applies');raise SystemExit(0)
    root=E.fromstring(z.read('sources/deeploc-2.xml'))
staging=tempfile.TemporaryDirectory(prefix='paper-reference-check-');asset_root=Path(staging.name)
expected=[clean(root.find('./front/article-meta/abstract/p'))]
tables=[]
def walk(parent):
    for c in parent:
        if c.tag=='p':expected.append(clean(c))
        elif c.tag in ('sec','list','list-item'):walk(c)
        elif c.tag=='fig':expected.append(clean(c.find('caption')))
        elif c.tag=='table-wrap':tables.append([[clean(cell) for cell in row]for row in c.findall('.//tbody/tr')])
for sec in root.findall('./body/sec')[:7]:walk(sec)
n=load_submission(ROOT/'library/deeploc-2',asset_root);validate(n,asset_root)
actual=[b['english']for s in n['sections']for b in s['blocks']]
assert actual==expected,'English paragraphs differ from the licensed source or their original order'
note_tables=[t for s in n['sections'] for b in s['blocks'] for t in b.get('tables',[])]
assert len(tables)==len(note_tables)==4
for source,table in zip(tables,note_tables):
    assert table['rows']==[row+['']*(len(table['headers'])-len(row))for row in source],'Numerical table cells changed'
bad=copy.deepcopy(n);bad['sections'][0]['blocks'][0]['highlights']=[{'kind':'thesis','text':'This is an invented English sentence.'}]
try:validate(bad,asset_root)
except ValueError:pass
else:raise AssertionError('Fabricated highlight accepted')
standalone=render_html(n,asset_root)
assert not re.search(r'<(?:script|link)[^>]+(?:src|href)=',standalone)
assert all(src.startswith('data:image/')for src in re.findall(r'<img src="([^"]+)"',standalone))
assert standalone.count('class="pair"')==len(expected)
print(f'Checked {len(expected)} exact English paragraph/caption units, 4 unchanged tables, highlight validation and offline HTML')

staging.cleanup()
