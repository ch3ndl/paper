"""Behavior checks for directory publishing, authoritative taxonomy and removal."""
import copy,importlib.util,json,shutil,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/paper-library-note/scripts'))
from repository_layout import read_taxonomy,load_library,load_submission

class DirectoryPublishing(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='paper-layout-test-');self.root=Path(self.tmp.name)
        self.note=json.loads((ROOT/'templates/note.example.json').read_text(encoding='utf-8'))
    def tearDown(self):self.tmp.cleanup()
    def paper(self,name='example-paper',taxonomy='分类: 生命科学 / 定位 / 方法\n标签:\n- 自定义甲\n- 自定义乙\n'):
        d=self.root/'library'/name;d.mkdir(parents=True)
        n=copy.deepcopy(self.note);n['slug']=name;n['category']='包内旧分类';n['tags']=['包内旧标签'];n['sections']=n['sections'][:1]
        for b in n['sections'][0]['blocks']:b.pop('figures',None)
        with zipfile.ZipFile(d/'result.zip','w')as z:z.writestr('notes/'+name+'.json',json.dumps(n,ensure_ascii=False))
        (d/'README.md').write_text('# 论文名\n作者及简介',encoding='utf-8');(d/'taxonomy.txt').write_text(taxonomy,encoding='utf-8');return d
    def test_external_taxonomy_overrides_package(self):
        d=self.paper();n=load_submission(d,self.root/'staging');self.assertEqual(n['category'],'生命科学 / 定位 / 方法');self.assertEqual(n['tags'],['自定义甲','自定义乙'])
    def test_one_category_only(self):
        with self.assertRaisesRegex(ValueError,'只能有一个分类'):read_taxonomy('分类: A\n分类: B\n标签:\n')
        with self.assertRaises(ValueError):read_taxonomy('分类: A // B\n标签:\n')
        self.assertEqual(read_taxonomy('分类: A / B\n标签:\n'),('A / B',[]))
    def test_custom_tags_and_deduplication(self):
        self.assertEqual(read_taxonomy('分类: A\n标签:\n- A:B\n- #自定义\n- A:B\n'),('A',['A:B','#自定义']))
    def test_invalid_zip_path_rejected(self):
        d=self.paper()
        with zipfile.ZipFile(d/'result.zip','a')as z:z.writestr('../../outside.txt','bad')
        with self.assertRaisesRegex(ValueError,'不安全'):load_submission(d,self.root/'staging')
    def test_missing_required_file_rejected(self):
        d=self.paper();(d/'taxonomy.txt').unlink()
        with self.assertRaisesRegex(ValueError,'taxonomy.txt'):load_submission(d,self.root/'staging')
    def test_removal_rebuilds_empty_site_without_stale_pages(self):
        d=self.paper();self.assertEqual(len(load_library(self.root/'library',self.root/'staging')),1)
        spec=importlib.util.spec_from_file_location('isolated_build',ROOT/'scripts/build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        for folder in ('assets','templates'):shutil.copytree(ROOT/folder,self.root/folder)
        mod.ROOT=self.root;mod.OUT=self.root/'_site';mod.build()
        self.assertTrue((mod.OUT/'papers/example-paper.html').exists());self.assertFalse((mod.OUT/'admin.html').exists());self.assertFalse((mod.OUT/'assets/admin.js').exists())
        index=(mod.OUT/'index.html').read_text(encoding='utf-8');self.assertIn('value="生命科学"',index);self.assertIn('value="生命科学 / 定位"',index)
        # The resolved target is the synthetic directory inside this temporary fixture.
        self.assertTrue(d.resolve().is_relative_to(self.root.resolve()));shutil.rmtree(d);mod.build()
        self.assertFalse((mod.OUT/'papers/example-paper.html').exists());self.assertEqual(json.loads((mod.OUT/'catalog.json').read_text(encoding='utf-8')),[])
        self.assertFalse((mod.OUT/'downloads/example-paper.html').exists())

if __name__=='__main__':unittest.main()
