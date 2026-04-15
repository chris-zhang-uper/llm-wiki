# OpenClaw 知识库上下文

> 此文件为 OpenClaw 提供只读访问知识库的入口信息。
> OpenClaw 只能读取，不能修改任何文件。

---

## 服务信息

| 项目 | 值 |
|------|------|
| 设备 | 树莓派 5 (ARM64) |
| 操作系统 | linux 6.12.75+rpt-rpi-2712 (arm64) |
| OpenClaw 版本 | 2026.4.9 (0512059) |
| Node.js 版本 | 22.22.2 |
| 仪表板 | http://127.0.0.1:18789/ |
| 网关 | ws://127.0.0.1:18789 |
| 进程 | openclaw (PID: 524729) |

---

## 知识库路径

> ⚠️ 以下路径为相对路径，OpenClaw 执行时需要先 cd 到知识库项目根目录。

| 文件 | 路径 | 用途 |
|------|------|------|
| 全局索引 | `wiki/index.md` | 从这里开始所有查询 |
| 操作日志 | `wiki/log.md` | 查看最近活动 |
| Wiki 页面 | `wiki/` | 所有编译后的知识 |
| 原始素材 | `raw/` | 原始来源文档 |
| 待审建议 | `pending/` | Lint 检查结果 |

---

## 使用规则

```
✅ 读取 wiki/index.md — 查询入口
✅ 读取 wiki/ 页面 — 获取知识内容
✅ 读取 raw/ 素材 — 获取原始资料
✅ 读取 pending/ 报告 — 查看 Lint 建议
❌ 写入任何文件 — 绝对禁止
```

---

## 查询流程

1. 先读 `wiki/index.md` 了解知识库全貌
2. 根据问题定位相关的 topic 和页面
3. 读取相关页面获取详细信息
4. 基于知识库内容辅助回答

---

## 定时任务配置

> ⚠️ 配置前，将下方 `/path/to/my-wiki` 替换为树莓派上的实际路径。

### 每日简报

```bash
openclaw cron add \
  --name "wiki-morning-briefing" \
  --cron "0 8 * * *" \
  --session isolated \
  --message "cd /path/to/my-wiki && 读取 wiki/index.md 获取知识库全貌，然后读取 wiki/ 下最近更新的 3-5 个页面，生成今日工作简报。简报内容：1) 最近更新的知识条目 2) 待审阅的 pending 内容 3) 建议关注的知识缺口。注意：你只能读取，不能修改任何文件。"
```

### 素材监控

```bash
openclaw cron add \
  --name "wiki-raw-monitor" \
  --every "2h" \
  --session isolated \
  --message "cd /path/to/my-wiki && 读取 wiki/log.md 获取已处理的素材列表，然后检查 raw/ 目录中是否有新增的 .md 文件。如果有未被处理的素材，发送通知提醒用户在 TRAE 中执行 Ingest。注意：你只负责检测和通知。"
```

### 知识库健康巡检

```bash
openclaw cron add \
  --name "wiki-health-check" \
  --cron "0 20 * * 0" \
  --session isolated \
  --message "cd /path/to/my-wiki && 读取 wiki/index.md 和 wiki/log.md，检查以下内容：1) 是否有超过 7 天未更新的活跃页面 2) pending/ 目录是否有未处理的 lint 建议 3) raw/ 目录中是否有超过 3 天未被处理的素材。生成简要报告。注意：你只能读取，不能修改任何文件。"
```

---

## 树莓派注意事项

| 项目 | 说明 |
|------|------|
| ARM64 兼容性 | Whisper 转录在 ARM64 上速度较慢，建议使用 `base` 模型或跳过音视频转录 |
| 存储空间 | 定期清理 `pending/` 目录中已处理的文件 |
| 内存限制 | 树莓派 5 内存有限，避免同时运行多个 Whisper 转录任务 |
| 自动启动 | 确保 OpenClaw 服务开机自启：`sudo systemctl enable openclaw` |
