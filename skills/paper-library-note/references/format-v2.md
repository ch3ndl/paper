# 双语逐段批注格式 v2

输出包含 `notes/<slug>.json`、`assets/images/<slug>/` 与自动生成的 `html/<slug>.html`。JSON 使用 UTF-8，所有字段为纯文本，高亮通过精确子串元数据表达，不嵌 HTML。

```json
{
  "schemaVersion": 2,
  "slug": "paper-short-name",
  "title": "中文论文名",
  "subtitle": "完整英文论文名",
  "course": "用户课程信息，或通用的学术论文精读栏目",
  "year": 2026,
  "category": "研究主题",
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
python scripts/package_note.py EXPORT_DIRECTORY SLUG OUTPUT.zip
```
会先校验再生成自包含 HTML 和 ZIP。单文件不超过 12 MiB，导入包整体不超过 30 MiB，最多 100 个文件。过大图片应在保持可读性的前提下压缩，不能删除关键数据面板来强行达标。
