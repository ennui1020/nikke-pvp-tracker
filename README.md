# NIKKE PVP Tracker ⚔️

记录《胜利女神：妮姬》特殊竞技场对战胜负的桌面工具。支持繁中角色名、拖拽组队、头像库、胜率统计。

## 🚀 快速开始（Windows）

### 编译版（推荐）

1. 下载最新 Release 的 zip 包
2. 解压后双击 `start.bat`
3. 浏览器自动打开 http://localhost:5000

### 源码启动

```bash
pip install -r requirements.txt
python app.py
```

浏览器打开 http://localhost:5000

## ✨ 功能一览

| 功能 | 说明 |
|------|------|
| **角色管理** | 185 SSR 角色库，支持编辑/删除/自定义头像 |
| **角色筛选** | 按企业/武器/代码/爆裂四维过滤角色池 |
| **拖拽组队** | 从角色池拖入 5 个槽位，组建我方/对方队伍 |
| **录战绩** | 选择进攻/防御，记录胜/负/平，附对手名和备注 |
| **头像库** | 角色配备对应头像，其余使用默认占位 |
| **批量导入** | 导入 JSON 格式的战绩记录 |
| **批量导出** | 导出为 JSON 或 CSV |
| **统计分析** | 总胜率、角色胜率排行、阵容胜率排行 |

## 📁 项目结构

```
nikke-pvp-tracker/
├── app.py                    # Flask 后端（单文件）
├── static/
│   ├── index.html            # 前端页面
│   └── default-avatar.png    # 默认占位头像
├── data/
│   ├── characters.json       # 用户角色数据（运行时生成）
│   ├── records.json          # 战绩记录（运行时生成）
│   └── nikke_characters.json # 185 SSR 角色数据库
├── avatars/                  # 角色头像图片库
├── scripts/
│   ├── merge_attributes.py      # 属性合并
│   └── import_characters.py     # 角色导入工具
├── nikke-pvp-tracker.spec    # PyInstaller 编译配置
├── requirements.txt
├── start.bat                 # Windows 一键启动
└── README.md
```

## 📊 数据存储

所有数据为纯 JSON，位于 `data/` 目录：

```
data/
├── records.json       # 战绩记录
├── characters.json    # 角色数据（含头像 URL）
└── nikke_characters.json  # 原始种子数据
```

## 🔧 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py

# 编译 Windows exe（需 Wine + PyInstaller）
wine pyinstaller nikke-pvp-tracker.spec
```

## 📦 依赖

- flask >= 3.0
- Pillow >= 10.0
- requests >= 2.30

## 📝 版本

**v0.5** — 头像库 + 同步修复 + 圆角显示 + 完整编译包
