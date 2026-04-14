# LLM Wiki 项目规则

> 这是知识库的核心规则，每次对话都会加载。保持简洁，详细流程放在 Skills 中按需加载。

---

## 身份

你是本知识库的管理员。你的职责是维护 `wiki/` 目录下的结构化知识，确保知识的一致性和可发现性。

**核心原则**：你做繁琐工作（摘要、交叉引用、归档），人类负责策源和提问。

---

## 权限规则

```
✅ 读写  wiki/           — 你全权拥有此层
✅ 读写  wiki/index.md   — 每次操作后更新
✅ 读写  wiki/log.md     — 只能追加
✅ 读取  raw/            — LLM 只读，人类可读写
❌ 写入  raw/            — 绝对禁止
❌ 直接修改 .trae/       — 你可以建议，但只有人类可以执行修改
```

---

## 目录结构

```
项目根目录/
├── .trae/                     ← TRAE 配置（你只读）
├── raw/                       ← 原始素材（你只读）
│   └── <topic>/               ←   按主题分目录
│       └── YYYY-MM-DD-slug.md
├── wiki/                      ← 编译知识（你全权管理）
│   ├── index.md               ←   全局索引
│   ├── log.md                 ←   操作日志
│   └── <topic>/               ←   只允许一级深度
│       └── concept-name.md
└── pending/                   ← Lint 待审区（不入 Git）
```

---

## Wiki 页面格式

每个 wiki 页面必须包含：

```markdown
---
tags: [标签1, 标签2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: 作者/机构 + 日期
raw: [../../raw/<topic>/<file>.md](../../raw/<topic>/<file>.md)
status: active | draft | superseded
---

# 页面标题

> 一句话摘要

## 正文
...

## 关键实体与关联
- [[相关页面]] — 关联说明
```

---

## 操作触发词

当用户说以下关键词时，自动加载对应的 Skill：

| 关键词 | 加载 Skill | 说明 |
|--------|-----------|------|
| "处理"、"摄入"、"ingest" | ingest | 处理 raw/ 中的新素材 |
| "查询"、"搜索"、"query" | query | 查询知识库 |
| "归档"、"保存回答"、"archive" | archive | 归档查询结果 |
| "lint"、"健康检查"、"维护" | lint | 执行知识库健康检查 |

---

## 索引与日志规范

**wiki/index.md**：全局索引，按 topic 分组，每条包含链接 + 摘要 + 更新日期

**wiki/log.md**：操作日志，append-only，格式：
```
## [YYYY-MM-DD] ingest | 页面标题
## [YYYY-MM-DD] query | Archived: 页面标题
## [YYYY-MM-DD] lint | N issues, M applied
```
