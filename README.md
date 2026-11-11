# Saline Papers

[打开论文网站](https://ch3ndl.github.io/paper/) · [在 GitHub 管理论文](library/)

论文网站用于浏览、搜索和精读。内容直接通过 GitHub 仓库管理，一篇论文一个目录，不设网站管理后台。

## 论文目录

```text
library/<论文标识>/
  result.zip     # Skill 输出的结果包
  README.md      # 论文名、作者、年份、简介、出处与阅读范围
  taxonomy.txt   # 唯一分类路径和多个自定义标签
```

上传、替换或删除论文目录，提交后自动发布。分类和标签只需修改 taxonomy.txt，不需要重做结果包。详见 [目录管理说明](library/README.md)。

## 精读格式与 Skill

逐段展示五色标注的英文原文、对应中文译文、右栏三项批注与详细讲解，结尾提供全文论证总览。支持移动端单栏与独立 HTML 下载。

Skill 位于 skills/paper-library-note/。输出结果包、简明 README 和 taxonomy.txt，可直接上传到 library/；分类只保留一条多层级路径，标签可自定义多个。论文图像包含在每篇结果包中，随仓库存储，构建时生成本站图片路径。

## 本地验证

```sh
python scripts/build.py
python scripts/check_site.py
python scripts/test_repository_layout.py
python scripts/check_bilingual.py
python -m http.server 8765 --directory _site
```

无需额外依赖。GitHub Settings → Pages → Source 选择 GitHub Actions。

DeepLoc 2.0 的英文与原表数字依据开放许可全文核对。代码使用 MIT；第三方论文文字与图像仍适用各自许可，详见文章署名。
