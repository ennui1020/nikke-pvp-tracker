# NIKKE PVP Tracker — ROADMAP

> 最後更新：2026-06-08
> 項目路徑：`/root/nikke-pvp-tracker/`
> 交付形式：Windows exe（PyInstaller onedir）/ 源代碼 Python

---

## 項目概述

NIKKE 特殊競技場（JJC）戰績記錄與分析工具。本地 Flask Web 應用，JSON 存儲，支援拖拽組隊、角色篩選、統計分析。

---

## 當前狀態

### 技術棧

| 層 | 技術 | 說明 |
|----|------|------|
| 後端 | Flask 3.x | 單文件 app.py |
| 前端 | 原生 JS + CSS | 單頁 index.html，無框架 |
| 存儲 | JSON 文件 | records.json / characters.json |
| 頭像 | 本地文件 / URL | 存於 avatars/ 目錄 |
| 打包 | PyInstaller | Windows onedir，24MB |
| 依賴 | flask, Pillow, requests | 極簡 |

### 已完成功能

#### 角色管理
- [x] 角色 CRUD（添加 / 編輯 / 刪除）
- [x] 185 SSR 角色一鍵導入（含繁中名 + 五維屬性）
- [x] 角色屬性：職業 / 企業 / 武器 / 代碼 / 爆裂
- [x] 頭像管理：URL 鏈接 / 本地圖片上傳
- [x] 別名支持（如「水阿」→「水冷阿尼斯」）

#### 錄戰績
- [x] 拖拽組隊（我方 5 人 + 對方 5 人）
- [x] 角色池篩選（企業 / 武器 / 代碼 / 爆裂）
- [x] 文字搜索（名稱 / 別名）
- [x] 選擇勝負 + 對手名
- [x] 批量導入 / 導出 JSON / CSV

#### 統計分析
- [x] 總勝率
- [x] 角色使用率 + 勝率排行
- [x] 陣容勝率排行
- [x] 對手勝率排行

#### 頭像默認
- [x] 自定義默認頭像（用戶提供）
- [x] SVG 兜底（服務器找不到圖時顯示）

#### 包裝交付
- [x] PyInstaller Windows exe 編譯
- [x] Wine 交叉編譯工具鏈
- [x] 啟動腳本 start.bat

---

## 已知問題 / 待修復

### P0 — 功能異常
- [ ] **角色導入後頭像 URL 為空**：爬蟲數據只含屬性，無頭像字段，導入後 `avatar_url` 為 null，全部顯示默認頭像
- [ ] **編輯角色頭像文件上傳不生效**：編輯模式下上傳頭像未調用 `/api/characters/<id>/avatar`

### P1 — 體驗缺陷
- [ ] **無窗口化啟動**：exe 附帶控制檯窗口，無法後臺運行
- [ ] **端口衝突**：無檢測，5000 端口被佔用直接報錯
- [ ] **數據無備份**：characters.json 被 seed 覆蓋時無備份

### P2 — 邊界情況
- [ ] **角色名特殊字符**：含 `'` 或 `"` 的角色在渲染時可能 HTML 注入
- [ ] **頭像 URL 跨域**：部分 Prydwen 圖片因 CORS 設置無法加載
- [ ] **大數據量效能**：5000+ 條戰績時列表渲染可能卡頓

---

## 後續優化方向

### 🟢 短期（1-2 次迭代）

#### 1. 頭像批量下載
- 利用現有 AVATAR_LOOKUP 映射表自動下載 Prydwen 頭像
- 後臺線程非阻塞下載，不阻塞頁面加載
- 下載進度提示

#### 2. 數據導入增強
- 角色導入時保留 `avatar_url` 來源信息
- 支持從用户提供的 URL 批量下載頭像
- seed API 增加 `?force=true` 參數強制覆蓋

#### 3. 窗口化啟動
- 使用 `pythonw.exe` 或 `--noconsole` PyInstaller 模式
- 系統托盤圖標指示運行狀態
- 托盤菜單：打開瀏覽器 / 停止服務

### 🟡 中期（3-5 次迭代）

#### 4. 數據可觀測性
- 自動數據備份（啟動時複製 `data/` → `data/backup/`）
- 操作日誌（誰、何時、做了什么）
- 數據完整性校驗（導入前驗證 JSON schema）

#### 5. 競技場對手管理
- 對手列表 + 最近對戰記錄
- 對手常用陣容統計
- 針對性陣容推薦（基於歷史勝率）

#### 6. 多端同步
- 數據導出到雲端（WebDAV / S3 / 自定義）
- 多設備共享角色數據
- 導入導出支持增量合並

### 🔴 長期（架構級）

#### 7. 數據庫遷移
- JSON → SQLite（避免大數據量性能問題）
- Flask → FastAPI（可選，性能提升）
- 數據庫 migration 腳本

#### 8. Web 端部署
- 支持 Docker 容器化部署
- 簡單的用戶認證（防止多人共用時衝突）
- Nginx 反向代理示例配置

#### 9. 自動更新
- GitHub Release 檢測
- 一鍵下載更新 exe
- 數據遷移腳本

---

## 構建與發布

### 開發環境

```bash
# 源碼啟動
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### Windows exe 構建

```bash
# 當前環境：Debian + Wine 10.0
# 工具鏈：Wine Python 3.12 embeddable + PyInstaller

wine C:\\Python312\\Scripts\\pyinstaller.exe ^
  C:\\project\\nikke-pvp-tracker.spec ^
  --distpath C:\\project\\dist ^
  --clean -y
```

### 發布包結構

```
nikke-pvp-tracker-dist/
├── nikke-pvp-tracker.exe    # 主程序（3.9MB）
├── _internal/               # PyInstaller 運行時（20MB）
│   ├── static/
│   │   ├── index.html       # 前端頁面
│   │   └── default-avatar.png
│   └── data/
│       └── nikke_characters.json  # 185 SSR 初始數據
├── 启动工具.bat
└── README.txt
```

### 發布清單

- [ ] exe 編譯通過
- [ ] 前端無 JS 錯誤
- [ ] 角色導入正常（185 SSR）
- [ ] 拖拽組隊 + 錄戰績
- [ ] 統計面板數據正確
- [ ] 默認頭像顯示正常
- [ ] 編輯角色保存正常
- [ ] 導入導出 JSON/CSV

---

## 附錄

### API 一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 前端頁面 |
| GET | `/api/characters` | 角色列表（支持篩選參數） |
| POST | `/api/characters` | 添加角色 |
| PUT | `/api/characters/<id>` | 編輯角色 |
| DELETE | `/api/characters/<id>` | 刪除角色 |
| POST | `/api/characters/<id>/avatar` | 上傳頭像 |
| POST | `/api/characters/seed` | 導入初始 185 SSR |
| GET | `/api/records` | 戰績列表 |
| POST | `/api/records` | 錄入戰績 |
| DELETE | `/api/records/<id>` | 刪除戰績 |
| GET | `/api/records/export?format=csv` | 導出戰績 |
| POST | `/api/records/import` | 導入戰績 |
| GET | `/api/stats/overview` | 總勝率統計 |
| GET | `/api/stats/by-unit` | 單體角色統計 |
| GET | `/api/stats/by-team` | 陣容統計 |
| GET | `/api/stats/by-opponent` | 對手統計 |
| GET | `/api/search/characters` | 角色搜索 |
| GET | `/api/enums` | 篩選枚舉值 |
| GET | `/default-avatar.png` | 默認頭像 |

### 角色數據字段

```json
{
  "id": "a1b2c3d4",          // 自動生成 uuid[:8]
  "name": "紅蓮",
  "alias": "scarlet",
  "class": "火力",
  "manufacturer": "朝圣者",
  "weapon": "AR",
  "code": "风压",
  "burst": "B3",
  "avatar_url": "/avatars/xxx.png"
}
```
