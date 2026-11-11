# 双语逐段批注格式 v2

创作时使用 `notes/<slug>.json` 与 `assets/images/<slug>/`，脚本自动生成独立 HTML。最终提交使用一论文一目录：

```text
library/<slug>/
  result.zip
  README.md
  taxonomy.txt
```

result.zip 内含 notes/<slug>.json、html/<slug>.html 和被引用的图片；网站只从 library 的论文子目录加载结果包。不要把包内目录散放到仓库根部。README 记录论文名、作者、简介、年份与出处。JSON 使用 UTF-8，所有字段为纯文本，高亮通过精确子串元数据表达，不嵌 HTML。

taxonomy.txt 是分类标签的唯一依据，构建时覆盖 JSON 中的 category 和 tags：

```text
分类: 生物信息学 / 蛋白质定位

标签:
- 蛋白语言模型
- 亚细胞定位
- 多标签分类
```

分类恰好一行，不能重复；“ / ”分隔父子层级，不能包含空层级。标签逐行可自定义多个，去重后保持顺序；无标签时保留空的“标签:”栏目。修改文本文件即可移动分类或增删标签，父分类筛选会包含后代文章，不需要维护额外分类注册表。目录、包内 JSON 文件名和 slug 必须一致。删除整个论文目录即可下架。

```json
{
  "schemaVersion": 2,
  "slug": "paper-short-name",
  "title": "中文论文名",
  "subtitle": "完整英文论文名",
  "authors": ["实际核实的作者名"],
  "course": "用户课程信息，或通用的学术论文精读栏目",
  "year": 2026,
  "category": "一级主题 / 二级主题",
  "tags": ["方法", "对象", "任务"],
  "updated": "2026-11-11",
  "status": "draft",
  "source": {
    "url": "https://doi.org/实际DOI",
    "citation": "实际作者、标题、期刊、年份、卷页与DOI",
    "license": "核实的英文原文及图片复用许可与署名；注明中文翻译和高亮为改编"
  },
  "summary": "一句话抓住论文主线，不代替逐段译文。",
  "coverage": "实际覆盖的原文、图表及未读取的补充材料。",
  "sections": [{
    "id": "introduction",
    "title": "引言",
    "originalHeading": "INTRODUCTION",
    "sourceLocation": "原文引言",
    "blocks": [{
      "heading": "该原段的阅读主题",
      "sourceLocation": "Introduction，第1段，实际版本页码（若可核实）",
      "english": "真实英文原段，不能使用生成式改写。",
      "translation": "完整对应的流畅中文学术译文。",
      "highlights": [{"kind": "term", "text": "english 中精确存在的英文片段"}],
      "annotation": {
        "function": "引出研究问题",
        "role": "该段在整体论证链中的具体位置。",
        "critique": "值得注意的论证技巧、证据边界或潜在漏洞。"
      },
      "explanation": "更详细的概念、方法、图表或结果解释，明确是 AI 辅助讲解。",
      "figures": [{
        "path": "assets/images/paper-short-name/figure-1.jpg",
        "alt": "清楚描述图中信息",
        "caption": "图号与对应中文图注、作者署名、改动说明。",
        "source": "https://原文稳定图像出处",
        "license": "核实的许可与署名"
      }],
      "tables": [{
        "caption": "Table 1 · 原文表名",
        "headers": ["指标", "方法A", "方法B"],
        "rows": [["F1", "原始数值", "原始数值"]],
        "note": "统计口径、原文表注与必要的表头展开说明。"
      }]
    }]
  }],
  "argumentMap": {
    "problem": "问题",
    "thesis": "论点",
    "evidence": "证据链",
    "rebuttal": "真实反驳或作者限定；不得虚构",
    "conclusion": "结论与适用范围",
    "claim": "作者核心主张的一句话版本",
    "strongest": "论证最强处一条，说明依据",
    "weakest": "论证最弱处一条，说明影响"
  }
}
```

上面是结构示例，不可把其中的说明文字当成论文事实。没有图片或表格时省略对应数组。

所有 english/translation/explanation/annotation 与论证总览字段必填。`highlights` 可为空，但全篇应有确实承担功能的五色标注；text 必须是对应 english 的精确子串，片段不能重叠（默认匹配第一次出现）。不要在中文译文中添加高亮标记。引文编号和原文文字错误可以保留并在讲解说明，不默默改写英文。

slug 与文件名一致，英文小写数字和连字符；章节 id 唯一。year 为四位整数，updated 为用户时区当天的 ISO 日期。status 默认 draft；reviewed 仅表示用户明确已人工核对，不能由 AI 阅读后自行赋予。网站仍兼容旧版 v1，但本 Skill 新生成的笔记一律为 v2，不再使用 englishParaphrase 代替原文。

图片为 PNG/JPEG/WebP，文件名英文，必须实际存在；表格每行与表头列数相同，原文多层表头可明确展开，不能改变列对应。`render_note.py` 以纯文本转义确保内容不会被当作脚本执行。

可直接运行：
```text
python scripts/package_note.py CREATION_DIRECTORY SLUG SUBMISSION_ROOT/library/SLUG
```
会先校验再生成自包含 HTML 与完整论文提交目录，其中 ZIP 固定名为 result.zip。已有 taxonomy.txt 和 README 不会被自动覆盖；用户要求更新这两者时应明确编辑。单文件不超过 12 MiB，结果包整体不超过 30 MiB，最多 100 个文件。过大图片应在保持可读性的前提下压缩，不能删除关键数据面板来强行达标。

目录校验示例（在 scripts 目录可导入模块）：
```python
from repository_layout import load_submission
load_submission("SUBMISSION_ROOT/library/SLUG", "TEMPORARY_VALIDATION_DIRECTORY")
```
