# NIKKE PVP Tracker ⚔️

記錄《勝利女神：妮姬》特殊競技場對戰勝負的桌面工具。支援繁中角色名、拖拽組隊、頭像庫、勝率統計。

## 🚀 快速開始（Windows）

### 編譯版（推薦）

1. 下載最新 Release 的 zip 包
2. 解壓後雙擊 `start.bat`
3. 瀏覽器自動打開 http://localhost:5000

### 源碼啟動

```bash
pip install -r requirements.txt
python app.py
```

瀏覽器打開 http://localhost:5000

## ✨ 功能一覽

| 功能 | 說明 |
|------|------|
| **角色管理** | 185 SSR 角色庫，支援編輯/刪除/自定義頭像 |
| **角色篩選** | 按企業/武器/代碼/爆裂四維過濾角色池 |
| **拖拽組隊** | 從角色池拖入 5 個槽位，組建我方/對方隊伍 |
| **錄戰績** | 選擇進攻/防禦，記錄勝/負/平，附對手名和備註 |
| **頭像庫** | 153 個角色配備 Prydwen 原版頭像，其餘使用默認佔位 |
| **批量導入** | 導入 JSON 格式的戰績記錄 |
| **批量導出** | 導出為 JSON 或 CSV |
| **統計分析** | 總勝率、角色勝率排行、陣容勝率排行 |

## 📁 項目結構

```
nikke-pvp-tracker/
├── app.py                    # Flask 後端（單文件）
├── static/
│   ├── index.html            # 前端頁面
│   └── default-avatar.png    # 默認佔位頭像
├── data/
│   ├── characters.json       # 用戶角色數據（運行時生成）
│   ├── records.json          # 戰績記錄（運行時生成）
│   └── nikke_characters.json # 185 SSR 角色數據庫
├── avatars/                  # 角色頭像圖片庫
├── scripts/
│   ├── scrape_characters_v4.py  # Prydwen 角色爬蟲
│   ├── merge_attributes.py      # 屬性合併
│   └── import_characters.py     # 角色導入工具
├── nikke-pvp-tracker.spec    # PyInstaller 編譯配置
├── requirements.txt
├── start.bat                 # Windows 一鍵啟動
└── README.md
```

## 🖼️ 頭像

- 153 個角色頭像自動從 Prydwen.gg CDN 下載
- 頭像存儲為 `.webp` 格式，圓角正方形顯示
- 首次運行後點擊「同步頭像」即可生效
- 其餘角色顯示彩色默認佔位頭像

## 📊 數據存儲

所有數據為純 JSON，位於 `data/` 目錄：

```
data/
├── records.json       # 戰績記錄
├── characters.json    # 角色數據（含頭像 URL）
└── nikke_characters.json  # 原始種子數據
```

## 🔧 開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動開發服務器
python app.py

# 編譯 Windows exe（需 Wine + PyInstaller）
wine pyinstaller nikke-pvp-tracker.spec

# 爬取最新角色數據
python scripts/scrape_characters_v4.py
```

## 📦 依賴

- flask >= 3.0
- Pillow >= 10.0
- requests >= 2.30

可選（角色爬蟲）：`beautifulsoup4`, `scrapling`

## 📝 版本

**v0.5** — 頭像庫 + 同步修復 + 圓角顯示 + 完整編譯包
