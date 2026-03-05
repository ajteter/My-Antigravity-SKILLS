# Antigravity Expert Skills Archive

这个仓库收集并优化了一系列用于 Antigravity/Claude 的常用 Skills，旨在提升 AI 在搜索、升级以及 UI 设计等领域的专业能力与交互体验。

## 核心技能列表

### 1. 🚀 Skills Discovery (优化版)
**目录**: `skills-discovery/`

这是基于官方版本的深度增强版。官方原版在搜索时往往忽略了关键的元数据，导致用户难以判断技能的时效性与可靠性。

**关键优化点：**
- **元数据全透传**：强制要求 AI 提取并显示 `author` (作者)、`sourceUrl` (源码地址)、`createdAt` (创建时间) 及 `updatedAt` (最后更新时间)。
- **时效性高亮**：新增 **CRITICAL** 规则，如果技能在最近一个月内有更新，AI 必须加粗或特别强调该日期（例如：`Updated: 2026-03-04 (Within 1 month!)`）。
- **来源透明化**：通过显示 GitHub 源码链接，方便用户在安装前进行代码审计，提升安全性。

### 2. 🔄 Skills Upgrade (自建技能)
**目录**: `skills-upgrade/`

这是一个完全自建的自动化技能，解决了 Antigravity 技能管理中“安装容易，维护难”的痛点。

**主要功能：**
- **全自动扫描**：一键扫描全局路径 (`~/.gemini/antigravity/skills/`) 下所有已安装的技能。
- **智能比对**：自动调用 `claude-plugins.dev` API 寻找每个技能对应的注册中心命名空间。
- **白名单保护 (Ignored Skills)**：内置 `IGNORED_SKILLS` 功能。对于类似 `skills-discovery` 这样具有本地深度定制化逻辑的技能，脚本会自动跳过升级，确保你的本地优化不会被官方版本覆盖。
- **无感升级**：使用 `npx skills-installer` 后台静默更新其他通用技能，保持工具链始终处于最新状态。

### 3. 🛠️ Skill Creator
**目录**: `skill-creator/`

专门用于开发、测试和迭代新技能的工作流。它通过引导 AI 捕获意图、编写 `SKILL.md`、运行测试用例并收集用户反馈，实现技能开发的标准化闭环。

### 4. 🎨 UI/UX Pro Max
**目录**: `ui-ux-pro-max/`

UI/UX 设计智能增强技能。内置 50 多种设计风格（如 Glassmorphism, Minimalism）和 20 多种配色方案，帮助 AI 生成极具美感且符合现代标准的网页和移动应用界面。

---

## 安装与使用

1. **手动安装**: 将对应的文件夹复制到你的 Antigravity 技能路径下（通常是 `~/.gemini/antigravity/skills/`）。
2. **使用技能**: 在 Antigravity 对话中直接提及相关任务（例如：“帮我搜一下关于 Docker 的技能” 或 “更新一下我所有的技能”），AI 将自动触发对应的 Skill。

## 维护建议

由于 `skills-discovery` 包含了高价值的本地优化，建议在使用 `skills-upgrade` 时保持 `skills-discovery` 在忽略名单中。
