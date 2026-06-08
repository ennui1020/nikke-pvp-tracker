# NIKKE PVP Tracker — ROADMAP

> 最后更新：2026-06-08
> 版本：v0.7
> 交付形式：Windows exe（PyInstaller onedir）/ 源代码 Python

---

## 项目概述

NIKKE 特殊竞技场（JJC）战绩记录与分析工具。本地 Flask Web 应用，JSON 存储，支持拖拽组队、角色筛选、统计分析。

---

## NOW — 当前优先

> 以下逐项待你确认，确认后开始执行。

- [x] **编辑角色头像上传不生效**
      编辑模式下上传头像可能未正确调用 API，需排查前端表单提交逻辑

- [x] **无窗口化启动**
      exe 附带控制台窗口 → 改为 `--noconsole` + 启动时自动打开浏览器

- [x] **数据安全：启动时自动备份**
      每次启动将 `data/` 复制到 `data/backup/` 目录

---

## NEXT — 下一阶段

- [x] **端口冲突检测**（5000 被占用时自动找可用端口）
- [x] **搜索优化**：支持按对手名 / 我方角色 / 对方角色搜索，允许使用别名搜索
- [x] **标⭐角色**：点击角色图标左上角标⭐/取消标⭐，新增筛选项按⭐过滤

---

## LATER — 远期规划

- [x] **UI 优化**：仿 NIKKE 游戏风格重新设计前端界面
- **爆裂显示优化**：爆裂 1/2/3/全 显示与游戏内同步

---

## API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 前端页面 |
| GET | `/api/characters` | 角色列表（支持筛选参数） |
| POST | `/api/characters` | 添加角色 |
| PUT | `/api/characters/<id>` | 编辑角色 |
| DELETE | `/api/characters/<id>` | 删除角色 |
| POST | `/api/characters/<id>/avatar` | 上传头像 |
| POST | `/api/characters/seed` | 导入初始 185 SSR |
| GET | `/sync_avatars` | 同步头像 URL 到角色数据 |
| GET | `/api/records` | 战绩列表 |
| POST | `/api/records` | 录入战绩 |
| DELETE | `/api/records/<id>` | 删除战绩 |
| GET | `/api/records/export?format=csv` | 导出战绩 |
| POST | `/api/records/import` | 导入战绩 |
| GET | `/api/stats/overview` | 总胜率统计 |
| GET | `/api/stats/by-unit` | 单体角色统计 |
| GET | `/api/stats/by-team` | 阵容统计 |
| GET | `/api/stats/by-opponent` | 对手统计 |
| GET | `/api/search/characters` | 角色搜索 |
| GET | `/api/enums` | 筛选枚举值 |
| GET | `/default-avatar.png` | 默认头像 |

## 版本历史

| 版本 | 日期 | 内容 |
|------|------|------|
| v0.7 | 2026-06-08 | NIKKE 游戏风格 UI 重设计（赛博暗色、青色荧光、角标装饰、网格底纹） |
| v0.6 | 2026-06-08 | 端口冲突检测 + 记录搜索优化 + 标⭐角色 + 启动自动备份 |
