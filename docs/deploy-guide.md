# 部署指南

> 从零开始部署你的 LLM Wiki 知识库。

---

## 环境要求

| 组件 | 要求 | 用途 |
|------|------|------|
| TRAE IDE | v3.0+ | AI 知识库管理 |
| Obsidian | 最新版 | 知识库查看和编辑 |
| OpenClaw | 已安装 | 定时任务和只读查询 |
| Python | 3.8+ | Lint 脚本执行 |
| Git | 任意版本 | 版本控制 |

---

## 部署步骤

### 第 1 步：初始化项目

```bash
# 复制项目到目标位置
cp -r my-wiki /your/target/path/
cd /your/target/path/my-wiki

# 初始化 Git
git init
git add -A
git commit -m "init: LLM Wiki v3.0"

# （可选）推送到远程仓库
git remote add origin <your-repo-url>
git push -u origin main
```

### 第 2 步：在 TRAE 中打开项目

1. 打开 TRAE IDE
2. 文件 → 打开文件夹 → 选择 my-wiki/
3. TRAE 会自动加载 `.trae/rules/project_rules.md` 作为项目规则
4. 验证：在对话中说"你是什么角色？"，应回答知识库管理员

### 第 3 步：运行验证

按 `Ctrl+Shift+P`，输入 `Tasks: Run Task`，选择 **Wiki: 验证配置**。

确保所有检查项通过。

### 第 4 步：初始化示例数据（可选）

运行 **Wiki: 初始化示例数据** Task，创建示例素材和 wiki 页面，帮助你理解工作流程。

### 第 5 步：配置 Obsidian

1. 打开 Obsidian
2. 打开文件夹 → 选择 my-wiki/
3. 设置 → 第三方插件 → 关闭安全模式
4. 安装插件：
   - **Dataview**（必须）— 用于 dashboard.md 的动态查询
   - **Web Clipper**（推荐）— 浏览器剪藏网页
5. 设置 → 文件与链接 → 附件文件夹路径 → 设为 `raw/assets/`

### 第 6 步：配置 OpenClaw（可选）

参考 `openclaw-context.md` 配置定时任务。

---

## 文件结构

```
my-wiki/
├── .trae/                        ← TRAE 配置
│   ├── rules/
│   │   └── project_rules.md      ← 核心规则（持续加载）
│   ├── skills/
│   │   ├── ingest/SKILL.md       ← Ingest 操作（按需加载）
│   │   ├── query/SKILL.md        ← Query 操作（按需加载）
│   │   ├── archive/SKILL.md      ← Archive 操作（按需加载）
│   │   └── lint/SKILL.md         ← Lint 操作（按需加载）
│   ├── agents/
│   │   └── wiki-health-reporter.md ← 健康报告 Agent
│   └── tasks.json                ← TRAE Tasks 定义
├── raw/                          ← 原始素材（LLM 只读）
├── wiki/
│   ├── index.md                  ← 全局索引
│   └── log.md                    ← 操作日志
├── pending/                      ← Lint 待审区（不入 Git）
├── scripts/
│   ├── lint-deterministic.py     ← 确定性 Lint 脚本
│   ├── verify-config.py          ← 配置验证脚本
│   └── init-examples.sh          ← 示例初始化脚本
├── openclaw-context.md           ← OpenClaw 只读上下文
├── QUICKSTART.md                 ← 快速入门指南
└── .gitignore
```

---

## 日常使用

### 摄入新素材

```
1. 浏览器看到好文章 → Obsidian Web Clipper → 保存到 raw/<topic>/
2. TRAE 中说："处理 raw/<topic>/xxx.md"
3. TRAE 执行 Ingest → 编译 wiki → 级联更新
4. Obsidian 中查看结果
```

### 查询知识

```
TRAE 中提问 → TRAE 读 index.md → 定位页面 → 综合回答
```

### 维护知识库

```
TRAE 中说："执行 Lint" → 检查问题 → 用户确认 → 应用修复
```

---

## 下一步

- 阅读 [QUICKSTART.md](QUICKSTART.md) 快速上手
- 根据你的领域调整 `.trae/rules/project_rules.md`
- 配置 OpenClaw 定时任务实现自动化
