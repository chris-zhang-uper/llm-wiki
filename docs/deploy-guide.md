# 部署指南

> 从零开始部署你的 LLM Wiki 知识库。

---

## 部署方式选择

| 方式 | 适用场景 | 优势 |
|------|----------|------|
| **本地部署** | 个人日常使用，轻量级 | 简单快速，无需服务器 |
| **远程服务器部署** | 团队协作、大量素材处理、24h 运行 | 多设备访问、GPU 转录、后台任务 |

---

## 方式一：本地部署

### 环境要求

| 组件 | 要求 | 用途 |
|------|------|------|
| TRAE IDE | v3.0+ | AI 知识库管理 |
| Obsidian | 最新版 | 知识库查看和编辑（可选） |
| OpenClaw | 已安装 | 定时任务和只读查询（可选） |
| Python | 3.8+ | 脚本执行 |
| Git | 任意版本 | 版本控制 |

### 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/chris-zhang-uper/llm-wiki.git
cd llm-wiki

# 2. 在 TRAE IDE 中打开此项目
#    文件 → 打开文件夹 → 选择 llm-wiki/
#    TRAE 会自动加载 .trae/rules/project_rules.md 作为项目规则

# 3. 验证：在对话中说"你是什么角色？"，应回答知识库管理员
```

### 安装可选依赖

```bash
# 基础依赖（处理 PDF/DOCX）
pip install pdfplumber python-docx --break-system-packages

# 视频链接处理
pip install yt-dlp --break-system-packages

# 音视频转录（处理本地音视频文件）
pip install openai-whisper --break-system-packages
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### 配置 Obsidian（可选）

1. 打开 Obsidian → 打开文件夹 → 选择 `llm-wiki/`
2. 安装插件：Dataview（动态查询）、Web Clipper（浏览器剪藏）
3. 设置 → 文件与链接 → 附件文件夹路径 → 设为 `raw/assets/`

### 配置 OpenClaw（可选）

参考 `openclaw-context.md` 配置定时任务。

---

## 方式二：远程服务器部署

### 适用场景

| 场景 | 说明 |
|------|------|
| 团队协作 | 多人通过 TRAE 远程访问同一知识库 |
| 大量素材处理 | 服务器 CPU/内存更强，批量处理更快 |
| 音视频转录 | 服务器 GPU 让 Whisper 转录速度提升 10-50 倍 |
| 24h 运行 | OpenClaw 定时任务无需本地电脑开机 |
| 多设备访问 | 任何设备通过 TRAE 远程连接访问 |

### 服务器要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Debian 10+ / Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| CPU | x64 处理器 | 4 核+ |
| 内存 | 1GB | 2GB+ |
| 磁盘 | 10GB | 50GB+（大量素材） |
| 网络 | 出站 HTTPS（端口 443） | 固定 IP |
| SSH | 已安装并运行 | SSH 密钥认证 |
| GPU（可选） | — | NVIDIA GPU（Whisper 转录加速） |

### 部署步骤

#### 第 1 步：连接远程服务器

在 TRAE IDE 中：

1. 点击左侧边栏的 **远程资源管理器** 图标
2. 点击 **"+"** 按钮
3. 输入连接命令：`ssh username@your-server-ip`
4. 点击 **"连接主机"**
5. 输入密码（或使用 SSH 密钥）

> 💡 快捷键：`Alt + Ctrl + O` 打开 Remote SSH 快捷操作面板

#### 第 2 步：在服务器上安装环境

连接成功后，在 TRAE 的终端中执行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y python3 python3-pip git ffmpeg

# 安装 Python 依赖
pip3 install pdfplumber python-docx yt-dlp --break-system-packages

# （可选）安装 Whisper（如果有 GPU）
pip3 install openai-whisper --break-system-packages

# 验证安装
python3 --version
ffmpeg -version
yt-dlp --version
```

#### 第 3 步：克隆项目

```bash
cd ~
git clone https://github.com/chris-zhang-uper/llm-wiki.git
cd llm-wiki
```

#### 第 4 步：在 TRAE 中打开远程项目

1. 连接远程服务器后，点击 **"打开文件夹"**
2. 选择服务器上的 `~/llm-wiki/` 目录
3. TRAE 会自动加载 `.trae/rules/project_rules.md`
4. 验证：在对话中说"你是什么角色？"

#### 第 5 步：运行验证

按 `Ctrl+Shift+P`，运行 **Wiki: 验证配置** Task。

#### 第 6 步：配置 OpenClaw 定时任务（推荐）

在服务器上配置 OpenClaw，实现 24h 自动化：

```bash
# 每日简报（每天 8:00）
openclaw cron add \
  --name "wiki-morning-briefing" \
  --cron "0 8 * * *" \
  --session isolated \
  --message "cd ~/llm-wiki && 读取 wiki/index.md 获取知识库全貌，生成今日工作简报。注意：你只能读取，不能修改任何文件。"

# 素材监控（每 2 小时）
openclaw cron add \
  --name "wiki-raw-monitor" \
  --every "2h" \
  --session isolated \
  --message "cd ~/llm-wiki && 读取 wiki/log.md 获取已处理的素材列表，检查 raw/ 目录中是否有新增文件。如果有，发送通知。注意：你只负责检测和通知。"
```

### 远程服务器上的日常使用

连接远程服务器后，使用方式与本地完全相同：

```
处理 raw/research/paper.pdf          ← 处理 PDF
处理 raw/podcast/episode.mp3         ← 转录音频
处理 https://youtube.com/watch?v=xxx ← 处理视频链接
批量处理 raw/work/                   ← 批量处理
查询关于 XX 的内容                    ← 查询知识库
执行 Lint                            ← 健康检查
```

所有操作都在远程服务器上执行，结果保存在服务器上。

### Obsidian 访问远程知识库

Obsidian 不支持直接通过 SSH 访问远程文件。有两种解决方案：

**方案 A：Git 同步（推荐）**

在服务器上设置 Git 自动提交，本地通过 Git 拉取：

```bash
# 服务器上：设置自动提交（每小时）
(crontab -l 2>/dev/null; echo "0 * * * * cd ~/llm-wiki && git add -A && git commit -m 'auto: hourly sync' && git push origin main") | crontab -
```

```bash
# 本地：拉取最新内容
git pull origin main
# 然后在 Obsidian 中查看
```

**方案 B：使用 Obsidian Git 插件**

1. 本地克隆仓库：`git clone user@server:~/llm-wiki.git`
2. 在 Obsidian 中打开本地克隆
3. 安装 Obsidian Git 插件，设置自动拉取间隔

### 常见问题

| 问题 | 解决方法 |
|------|----------|
| 连接失败（错误码 1003/3001） | 检查服务器系统版本（需 Debian 10+ / Ubuntu 20.04+） |
| 连接失败（错误码 2001） | 检查网络连通性，确保服务器可访问 |
| 连接超时 | 避免使用大写主机名，将默认 shell 改为 bash 或 zsh |
| 服务启动失败 | `rm -rf ~/.trae-cn-server/bin` 后重新连接 |
| 通过跳板机连接 | 在 settings.json 中添加代理配置 |
| Whisper 转录很慢 | 安装 CUDA 驱动和 GPU 版 PyTorch |

---

## 文件结构

```
llm-wiki/
├── .trae/                        ← TRAE 配置
│   ├── rules/project_rules.md    ← 核心规则
│   ├── skills/                   ← 操作技能
│   ├── agents/                   ← 独立 Agent
│   ├── settings.json             ← 性能配置
│   └── tasks.json                ← TRAE Tasks
├── raw/                          ← 原始素材（LLM 只读）
├── wiki/                         ← 编译知识（LLM 管理）
├── pending/                      ← Lint 待审区
├── scripts/                      ← 辅助脚本
├── obsidian/                     ← Obsidian 专用
├── openclaw-context.md           ← OpenClaw 配置
├── QUICKSTART.md                 ← 快速入门
├── README.md                     ← 项目主页
└── docs/                         ← 文档
```

---

## 日常使用

### 摄入新素材

```
1. 素材来源 → 放入 raw/<topic>/（拖拽/剪藏/下载）
2. TRAE 中说："处理 raw/<topic>/xxx" 或 "批量处理 raw/<topic>/"
3. TRAE 自动：格式转换 → 编译 Wiki → 级联更新
4. Obsidian 中查看结果
```

### 查询知识

```
TRAE 中提问 → 读 index.md → 定位页面 → 综合回答
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
