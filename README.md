# Saline Papers

论文阅读与收集网站，部署在 GitHub Pages。

- 论文库：标题与关键词搜索、分类、标签、排序、本机收藏。
- 阅读页：全站导航、原文顺序讲解与独立批注、目录、阅读进度、专注模式、图像放大、打印。
- 管理页：连接仅限本仓库的 GitHub 细粒度令牌，导入 ZIP/JSON、上传图片、修改分类、标签与正文，原子提交到 main 后自动构建发布。
- Skill：`skills/paper-library-note/`，输出与网站一致的 JSON + 本地图片 ZIP 包。

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

附件迁移示例保留原有内容并标记待核对。不能将示例的覆盖深度当作新 Skill 的精读质量标准。论文图像各自保留来源和许可；本站代码使用 MIT 许可，第三方论文内容不包含在代码许可中。
