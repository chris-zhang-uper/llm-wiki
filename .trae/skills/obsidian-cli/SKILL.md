---
name: obsidian-cli
description: Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes. Invoke when user asks to interact with their Obsidian vault, manage notes, search vault content, or perform vault operations from the command line.
---

# Obsidian CLI Skill

Use the obsidian CLI to interact with a running Obsidian instance. Requires Obsidian to be open.

## Command reference

Run `obsidian help` to see all available commands. This is always up to date.

Full docs: https://help.obsidian.md/cli

## Syntax

Parameters take a value with `=`. Quote values with spaces:
```
obsidian create name="My Note" content="Hello world"
```

Flags are boolean switches with no value:
```
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

## File targeting

Many commands accept `file` or `path` to target a file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

## Vault targeting

Commands target the most recently focused vault by default. Use `vault=<name>` as the first parameter to target a specific vault:
```
obsidian vault="My Vault" search query="test"
```

## Common patterns

```
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append file="My Note" content="New line"
obsidian search query="search term" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="My Note"
```

Use `--copy` on any command to copy output to clipboard. Use `silent` to prevent files from opening. Use `total` on list commands to get a count.

## Plugin development

### Develop/test cycle

After making code changes to a plugin or theme, follow this workflow:

1. **Reload the plugin** to pick up changes:
   ```
   obsidian plugin:reload id=my-plugin
   ```

2. **Check for errors** — if errors appear, fix and repeat from step 1:
   ```
   obsidian dev:errors
   ```

3. **Verify visually** with a screenshot or DOM inspection:
   ```
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```

4. **Check console output** for warnings or unexpected logs:
   ```
   obsidian dev:console level=error
   ```

### Additional developer commands

- **Run JavaScript** in the app context:
  ```
  obsidian eval code="app.vault.getFiles().length"
  ```

- **Inspect CSS values**:
  ```
  obsidian dev:css selector=".workspace-leaf" prop=background-color
  ```

- **Toggle mobile emulation**:
  ```
  obsidian dev:mobile on
  ```

Run `obsidian help` to see additional developer commands including CDP and debugger controls.

## Usage Examples

- Creating a new note: `obsidian create name="New Note" content="# Hello World"`
- Reading a note: `obsidian read file="My Note"`
- Searching: `obsidian search query="keyword"`
- Daily note: `obsidian daily:read` or `obsidian daily:append content="- [ ] Task"`
- Managing properties: `obsidian property:set name="status" value="done" file="My Note"`
- Viewing backlinks: `obsidian backlinks file="My Note"`
- Plugin development: `obsidian plugin:reload id=my-plugin`
- Taking screenshot: `obsidian dev:screenshot path=screenshot.png`

## Obsidian CLI 完整路径配置

### Obsidian 安装路径

根据您的系统，Obsidian CLI 的完整路径为：
```
H:\Obsidian\Obsidian.exe
```

### 使用方法

#### 1. 直接使用完整路径

在命令前添加完整路径：
```bash
H:\Obsidian\Obsidian.exe files
H:\Obsidian\Obsidian.exe read file="index"
H:\Obsidian\Obsidian.exe daily:append content="- [ ] 新任务"
```

#### 2. 创建批处理文件（推荐）

创建一个 `obsidian.bat` 文件：

1. 在 `H:\Obsidian\` 目录或 `C:\Users\晓光\AppData\Roaming\npm\` 目录创建 `obsidian.bat`

2. 文件内容：
```batch
@echo off
"H:\Obsidian\Obsidian.exe" %*
```

3. 确保该目录在系统 PATH 中（`C:\Users\晓光\AppData\Roaming\npm\` 已在 PATH 中）

#### 3. 添加到 PATH 环境变量

如果批处理文件不起作用，手动添加：

1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 点击「高级」选项卡 → 「环境变量」
3. 在「用户变量」中找到 `Path`，点击「编辑」
4. 点击「新建」，添加：`H:\Obsidian\`
5. 点击「确定」保存

### TRAE 中的使用方式

**重要**：从 Obsidian 1.12.2+ 版本开始，CLI 命令默认是静默操作的（不打开文件窗口）。

配置完成后，在 TRAE 中可以直接使用：
```
obsidian files
obsidian read file="index"
obsidian search query="关键词"
```

使用 `open` 标志可以打开文件：
```
obsidian read file="index" open
obsidian create name="新笔记" content="# 内容" open
```

## Installation (if needed)

### 方案一：obsidian-http-mcp（推荐）

这是专门为AI助手（如Claude Code、Trae）设计的MCP服务器：

1. **在Obsidian中启用Local REST API插件**：
   - 打开Obsidian → 设置 → 社区插件
   - 搜索并安装 "Local REST API"
   - 启用插件，启用"Non encrypted (HTTP) API"
   - 复制API密钥

2. **安装obsidian-http-mcp**：
   ```bash
   npm install -g obsidian-http-mcp
   ```

3. **设置配置**：
   ```bash
   obsidian-http-mcp --setup
   # 输入您的Obsidian API密钥
   ```

4. **启动服务器**：
   ```bash
   obsidian-http-mcp
   ```

### 方案二：mcp-obsidian-cli

使用MCP协议，不需要API密钥：

1. **确保Obsidian的CLI插件已启用**

2. **运行**：
   ```bash
   npx -y mcp-obsidian-cli
   ```

3. **配置环境变量**：
   ```bash
   export OBSIDIAN_VAULT="你的仓库名称"
   ```

For more details, visit: https://help.obsidian.md/cli