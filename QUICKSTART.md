# 快速入门指南

> 5 分钟内让你的知识库运转起来。

---

## 第一步：验证配置

在 TRAE 中打开此项目后，按 `Ctrl+Shift+P`（Mac: `Cmd+Shift+P`），输入 `Tasks: Run Task`，选择 **Wiki: 验证配置**。

你应该看到所有检查项都显示 ✓。

---

## 第二步：初始化示例素材

运行 **Wiki: 初始化示例数据** Task，这会创建 3 篇示例素材到 `raw/demo/` 目录。

> ⚠️ 注意：此步骤只创建原始素材，不创建 wiki 页面。wiki 页面由你在下一步通过 Ingest 流程自行创建。

---

## 第三步：体验完整工作流

按以下顺序在 TRAE 对话中执行，体验知识库的核心能力：

### 3.1 体验 Ingest（摄入素材）

```
处理 raw/demo/2026-04-04-karpathy-llm-wiki.md
```

**预期效果**：
- TRAE 读取素材，讨论要点
- 在 `wiki/demo/` 下创建新页面（如 `llm-wiki-pattern.md`）
- 更新 `wiki/index.md` 和 `wiki/log.md`

### 3.2 体验级联更新（Cascade Updates）

```
处理 raw/demo/2026-04-10-community-wiki-implementation.md
```

**预期效果**：
- TRAE 创建新页面（如 `wiki-implementation.md`）
- **同时更新** 3.1 中创建的页面（补充社区实践的具体细节）
- 在两个页面之间建立 `[[双向链接]]`
- `wiki/log.md` 中出现 `- Updated: llm-wiki-pattern` 记录

### 3.3 体验矛盾标注

```
处理 raw/demo/2026-04-12-critique-llm-wiki.md
```

**预期效果**：
- TRAE 创建新页面（如 `llm-wiki-critique.md`）
- **在已有页面中标注矛盾**（如："Karpathy 称维护成本接近零，但批判文章认为被低估"）
- 矛盾以 `> ⚠️ **矛盾标注**：...` 格式呈现

### 3.4 体验 Query（查询）

```
查询知识库中关于 LLM Wiki 维护成本的内容
```

**预期效果**：
- TRAE 读取 `wiki/index.md` 定位相关页面
- 综合多个页面回答，展示矛盾双方的观点
- 询问是否归档

### 3.5 体验 Lint（健康检查）

```
执行 Lint
```

**预期效果**：
- TRAE 深度阅读所有 wiki 页面
- 报告发现的问题（如孤立链接、知识缺口等）
- 建议下一步行动

---

## 第四步：在 Obsidian 中查看

1. 打开 Obsidian
2. 打开此项目文件夹
3. 打开 `wiki/demo/` 目录，查看生成的页面
4. 打开**图谱视图**（右上角图标），查看页面之间的关联
5. 打开 `wiki/index.md`，查看全局索引

---

## 第五步：添加你自己的素材

### 方式 A：使用 Obsidian Web Clipper

1. 安装 Obsidian Web Clipper 浏览器扩展
2. 在网页上点击扩展图标
3. 保存到 `raw/<topic>/` 目录

### 方式 B：手动创建

1. 在 `raw/` 下创建 topic 目录（如 `raw/work/`）
2. 创建 markdown 文件，命名格式：`YYYY-MM-DD-标题.md`
3. 在文件开头添加元数据：

```markdown
---
source: https://example.com/article
collected: 2026-04-13
published: 2026-04-10
---

# 文章标题

（粘贴文章内容）
```

---

## 常用命令速查

| 你说的话 | TRAE 做的事 |
|----------|-------------|
| "处理 raw/xxx.md" | 执行 Ingest，编译素材到 wiki |
| "查询关于 XX 的内容" | 搜索 wiki 并综合回答 |
| "归档这个回答" | 将分析保存为 wiki 页面 |
| "执行 Lint" | 健康检查知识库 |
| "生成健康报告" | 输出统计和状态报告 |

---

## 下一步

- 🔧 根据你的领域调整 `.trae/rules/project_rules.md` 中的规则
- 📊 在 Obsidian 中安装 Dataview 插件以使用 dashboard.md
- ⏰ 配置 OpenClaw 定时任务（参考 `openclaw-context.md`）
