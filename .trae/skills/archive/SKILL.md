---
name: archive
description: 将查询产生的综合分析归档为独立页面。触发词：归档、保存回答、archive、加入知识库
---

# Archive 操作流程

## 触发条件

- 用户说"保存这个回答"、"归档"
- 用户确认 Query 操作中的归档建议

## 操作步骤

### 1. 创建归档页面
将查询产生的综合分析写入新的 wiki 页面：
- 文件名反映查询主题，如 `transformer-architectures-overview.md`
- 放入最相关的 topic 目录

### 2. 归档页面特殊格式

归档页面使用独立的 frontmatter 格式：

```markdown
---
tags: [archived, 标签1]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: wiki:页面A, wiki:页面B
status: archived
---

# 页面标题

> [Archived] 一句话摘要

## 正文
（综合分析内容）

## 来源页面
- [[页面A]]
- [[页面B]]
```

### 3. 关键规则 ⭐

- `sources` 字段格式为 `wiki:页面名`，表示来源是 wiki 页面而非 raw 文件
- 没有 `raw` 字段
- 在 `wiki/index.md` 的 Summary 前加 `[Archived]` 前缀
- **Archive 页面是 point-in-time 快照，后续 Ingest 的级联更新不会修改它**

### 4. 更新索引和日志
- 更新 `wiki/index.md`
- 追加 `wiki/log.md`：
```
## [YYYY-MM-DD] query | Archived: <归档页面标题>
```

## 完成确认

告知用户：
- 归档页面已创建：`wiki/<topic>/<name>.md`
- 提醒：此页面是快照，不会被后续更新自动修改
