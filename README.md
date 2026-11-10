# Saline Papers

论文阅读与收集网站，部署在 GitHub Pages。

- 论文库：标题与关键词搜索、分类、标签、排序、本机收藏。
- 阅读页：全站导航、逐段英文原文、对应中文译文、五色标注与独立批注、目录、阅读进度、专注模式、图像放大、打印。
- 管理页：连接仅限本仓库的 GitHub 细粒度令牌，导入 ZIP/JSON、上传图片、修改分类、标签与正文，原子提交到 main 后自动构建发布。
- Skill：`skills/paper-library-note/`，输出逐段双语批注 v2 JSON、自包含 HTML 和本地图片 ZIP 包。

## 发布笔记

管理页导入 Skill 输出的 ZIP，检查后保存；或将文件包内 `notes/` 与 `assets/images/` 合并到仓库同名目录并提交。不要上传令牌或私人资料。管理页凭据只在页面内存中保存。

本地构建，无额外依赖：

```sh
python scripts/build.py
python scripts/check_site.py
python -m http.server 8765 --directory _site
```

GitHub Settings → Pages → Source 选择 GitHub Actions。工作流构建失败时不会替换已发布版本。

域名启用步骤见站点“阅读与发布”。未确认 Cloudflare 配置前使用 https://ch3ndl.github.io/paper/ 。

DeepLoc 2.0 已依据 CC BY 4.0 许可的 JATS 全文重做为逐段双语批注，包含 27 个原文段落与图注单元及四张主表。英文和表格数值与 sources/deeploc-2.xml 自动比对，中文译文及评议仍属 AI 辅助阅读。论文图像各自保留来源和许可；本站代码使用 MIT 许可，第三方论文内容不包含在代码许可中。
