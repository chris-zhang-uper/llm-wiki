# 知识库仪表盘

> 在 Obsidian 中打开此页面，快速了解知识库状态。

---

## 📊 统计概览

### Wiki 页面总数
```dataview
LIST
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
SORT file.name ASC
```

### 最近更新的页面
```dataview
LIST
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
SORT updated DESC
LIMIT 10
```

### 归档页面
```dataview
LIST
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
WHERE contains(sources, "Archived")
SORT updated DESC
```

---

## 🔍 健康状态

### 孤立页面（无入链）
```dataview
LIST
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
WHERE length(file.inlinks) = 0
SORT file.name ASC
```

### 待审阅的 Lint 建议
```dataview
LIST
FROM "pending"
SORT file.name DESC
```

---

## 🏷️ 按标签浏览

### 所有标签
```dataview
TABLE length(rows) AS 页面数
FROM "wiki"
WHERE file.name != "index" AND file.name != "log"
FLATTEN tags AS tag
GROUP BY tag
SORT tag ASC
```

---

## 📅 最近操作

> 以下内容来自 wiki/log.md，显示最近 10 条操作记录。

```dataviewjs
const logFile = app.vault.getAbstractFileByPath("wiki/log.md");
if (logFile) {
    const content = await app.vault.read(logFile);
    const entries = content.split("## [").filter(e => e.trim());
    const recent = entries.slice(-10).reverse();
    for (const entry of recent) {
        dv.paragraph("## [" + entry.split("\n")[0]);
    }
} else {
    dv.paragraph("_wiki/log.md 尚无记录_");
}
```
