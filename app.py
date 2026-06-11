#!/usr/bin/env python3
"""
NIKKE PVP Tracker - 竞技场战绩记录与分析工具
Flask 单文件后端，JSON 本地存储
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory, send_file, Response

# ──────────────────────────────────────
# 路径常量（支持 PyInstaller 打包）
# ──────────────────────────────────────
import sys as _sys
# Windows cp1252 修复：在 print() 前配置 stdout/stderr 编码
if getattr(_sys, 'frozen', False) and _sys.platform == 'win32':
    try:
        _sys.stdout.reconfigure(encoding='utf-8')
        _sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if getattr(_sys, 'frozen', False):
    # 从环境变量或 exe 所在目录读取
    BASE_DIR = Path(os.environ.get('NIKKE_PVP_BASE', _sys.executable)).parent \
        if os.environ.get('NIKKE_PVP_BASE') else Path(_sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"

# 頭像目錄：先檢查 exe 同級，再檢查 PyInstaller _internal
AVATAR_DIR = BASE_DIR / "avatars"
if not AVATAR_DIR.exists() and getattr(_sys, '_MEIPASS', None):
    _alt = Path(_sys._MEIPASS) / "avatars"
    if _alt.exists():
        AVATAR_DIR = _alt

CHARACTERS_FILE = DATA_DIR / "characters.json"
RECORDS_FILE = DATA_DIR / "records.json"

for d in [DATA_DIR, AVATAR_DIR]:
    d.mkdir(exist_ok=True)

# ──────────────────────────────────────
# 数据层（放在前面，後續初始化邏輯要用）
# ──────────────────────────────────────

def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default
    return default


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_characters():
    return _load_json(CHARACTERS_FILE, [])


def save_characters(chars):
    _save_json(CHARACTERS_FILE, chars)


def load_records():
    return _load_json(RECORDS_FILE, [])


def save_records(records):
    _save_json(RECORDS_FILE, records)


def _find_duplicate_character(name, alias=None, exclude_id=None):
    chars = load_characters()
    for c in chars:
        if exclude_id and c.get("id") == exclude_id:
            continue
        if c.get("name") == name or c.get("alias") == name:
            return c
        if alias and (c.get("name") == alias or c.get("alias") == alias):
            return c
    return None


# 查找 nikke_characters.json（支援開發環境和 PyInstaller 打包）
def _find_seed_file():
    candidates = [
        BASE_DIR / "data" / "nikke_characters.json",
    ]
    if getattr(_sys, '_MEIPASS', None):
        candidates.append(Path(_sys._MEIPASS) / "data" / "nikke_characters.json")
    for p in candidates:
        if p.exists():
            return p
    return None

SEED_FILE = _find_seed_file()

# 首次啟動：全量導入
if SEED_FILE and not CHARACTERS_FILE.exists():
    with open(str(SEED_FILE), "r", encoding="utf-8") as f:
        raw = json.load(f)
    for c in raw:
        if "id" not in c or not c["id"]:
            c["id"] = str(uuid.uuid4())[:8]
    with open(str(CHARACTERS_FILE), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"[init] 已自動導入 {SEED_FILE} → {CHARACTERS_FILE}（補了 id）")

# 已有 characters.json => 同步 avatar_url（確保新下載的頭像生效）
if SEED_FILE and CHARACTERS_FILE.exists():
    with open(str(SEED_FILE), "r", encoding="utf-8") as f:
        seed_data = json.load(f)
    # 建立 seed 映射表: name -> avatar_url
    seed_map = {}
    for c in seed_data:
        seed_map[c["name"]] = c.get("avatar_url") or None
        if c.get("alias"):
            seed_map[c["alias"]] = c.get("avatar_url") or None

    chars = _load_json(CHARACTERS_FILE, [])
    updated = 0
    for c in chars:
        url = seed_map.get(c["name"]) or seed_map.get(c.get("alias", ""))
        if url and c.get("avatar_url") != url:
            c["avatar_url"] = url
            updated += 1
    if updated:
        _save_json(CHARACTERS_FILE, chars)
        print(f"[init] 已同步 {updated} 個角色的 avatar_url")

# 首次啟動默認頭像
default_avatar = AVATAR_DIR / "default.png"
if not default_avatar.exists():
    avatar_src_candidates = [
        BASE_DIR / "static" / "default-avatar.png",
    ]
    if getattr(_sys, '_MEIPASS', None):
        avatar_src_candidates.append(Path(_sys._MEIPASS) / "static" / "default-avatar.png")
    for src in avatar_src_candidates:
        if src and src.exists():
            import shutil
            shutil.copy2(str(src), str(default_avatar))
            print(f"[init] 已複製默認頭像 {src} → {default_avatar}")
            break

"""
角色分类枚举
"""
CHAR_CLASSES = ["火力", "防御", "支援"]
CHAR_MANUFACTURERS = ["极乐净土", "泰特拉", "米西利斯", "朝圣者", "反常"]
CHAR_WEAPONS = ["AR", "SMG", "SG", "SR", "MG", "RL"]
CHAR_CODES = ["风压", "水冷", "铁甲", "燃烧", "电击", "无"]
CHAR_BURSTS = ["B1", "B2", "B3", "全"]



def find_character(name_or_id):
    chars = load_characters()
    for c in chars:
        if c["id"] == name_or_id:
            return c
        if c["name"] == name_or_id:
            return c
        if c.get("alias") == name_or_id:
            return c
    return None


def resolve_team_names(team_list):
    """将别名/ID 列表解析为角色名列表（支持简繁匹配）"""
    resolved = []
    chars = load_characters()
    name_map = {}
    for c in chars:
        name_map[c["id"]] = c["name"]
        name_map[c["name"]] = c["name"]
        if c.get("alias"):
            name_map[c["alias"]] = c["name"]

    for item in team_list:
        item = item.strip()
        if item in name_map:
            resolved.append(name_map[item])
        else:
            # 简繁模糊匹配：如果输入是简体，尝试匹配繁体
            matched = False
            for key, val in name_map.items():
                if _is_similar(item, key):
                    resolved.append(val)
                    matched = True
                    break
            if not matched:
                resolved.append(item)
    return resolved


def _norm(text):
    """统一文本对比基准：NFKC + 小写 + 去空格"""
    import unicodedata
    return unicodedata.normalize("NFKC", text.strip().lower())


def _is_similar(a, b):
    """判断两个文本是否视为同一角色名（处理繁简差异 + 分隔符差异）"""
    try:
        from zhconv import convert
        variants_a = {a, convert(a, "zh-hans"), convert(a, "zh-hant")}
        variants_b = {b, convert(b, "zh-hans"), convert(b, "zh-hant")}
        # 精确匹配
        for va in variants_a:
            for vb in variants_b:
                if _norm(va) == _norm(vb):
                    return True
        # 宽松匹配：去除常见的分隔符（: ：·）后再比
        import re
        for va in variants_a:
            stripped_a = re.sub(r"[:：·\s]", "", _norm(va))
            for vb in variants_b:
                stripped_b = re.sub(r"[:：·\s]", "", _norm(vb))
                if stripped_a == stripped_b:
                    return True
    except ImportError:
        return _norm(a) == _norm(b)
    return False


def _canonical_variants(text):
    try:
        from zhconv import convert
        variants = {text, convert(text, 'zh-hans'), convert(text, 'zh-hant')}
    except Exception:
        variants = {text, _to_simplified(text), _to_traditional(text)}
    return {v.lower() for v in variants if v}


def _matches_query(text, q):
    import re
    if not text or not q:
        return False
    q_variants = _canonical_variants(q)
    text_variants = _canonical_variants(text)
    for qv in q_variants:
        norm_q = _norm(qv)
        stripped_q = re.sub(r"[:：·\s]", "", norm_q)
        for tv in text_variants:
            norm_tv = _norm(tv)
            if norm_q in norm_tv:
                return True
            if stripped_q and stripped_q in re.sub(r"[:：·\s]", "", norm_tv):
                return True
    return False


# 简繁字符映射表（zhconv 不可用时的备用方案）
_SIMPLIFIED_TABLE = str.maketrans({
    '愛': '爱', '蓮': '莲', '紅': '红', '長': '长', '髮': '发', '發': '发',
    '麗': '丽', '絲': '丝', '貝': '贝', '爾': '尔', '聖': '圣', '潔': '洁',
    '亞': '亚', '瑪': '玛', '維': '维', '爾': '尔', '爾': '尔',
    '緋': '绯', '蒼': '苍', '鋒': '锋', '颯': '飒', '華': '华',
    '櫻': '樱', '純': '纯', '戀': '恋', '戀': '恋',
    '極': '极', '樂': '乐', '淨': '净', '土': '土',
    '泰': '泰', '特': '特', '拉': '拉',
    '米': '米', '西': '西', '利': '利', '斯': '斯',
    '朝': '朝', '聖': '圣', '者': '者',
    '反': '反', '常': '常',
    '風': '风', '壓': '压', '水': '水', '冷': '冷',
    '鐵': '铁', '甲': '甲', '燃': '燃', '燒': '烧',
    '電': '电', '擊': '击', '無': '无',
    '火': '火', '力': '力', '防': '防', '禦': '御',
    '支': '支', '援': '援',
    '軍': '军', '火': '火', '衝': '冲', '槍': '枪',
    '步': '步', '機': '机', '關': '关',
    '全': '全',
})
_TRADITIONAL_TABLE = str.maketrans({v: k for k, v in _SIMPLIFIED_TABLE.items()})

def _to_simplified(text):
    return text.translate(_SIMPLIFIED_TABLE)


def _to_traditional(text):
    return text.translate(_TRADITIONAL_TABLE)

AVATAR_LOOKUP = {
    # 常用 PVP 角色名 → Prydwen 图标 ID
    "红莲": "scarlet",
    "scarlet": "scarlet",
    "哈兰": "harran",
    "harran": "harran",
    "长发公主": "rapunzel",
    "长发": "rapunzel",
    "rapunzel": "rapunzel",
    "诺雅": "noah",
    "noah": "noah",
    "豺狼": "jackal",
    "jackal": "jackal",
    "森提": "centi",
    "centi": "centi",
    "水阿": "anis-summer",
    "水阿尼斯": "anis-summer",
    "阿尼斯": "anis",
    "anis": "anis",
    "饼干": "biscuit",
    "biscuit": "biscuit",
    "罗珊娜": "rosanna",
    "rosanna": "rosanna",
    "桑迪": "sandi",
    "sandi": "sandi",
    "白兔": "blanc",
    "blanc": "blanc",
    "黑兔": "noir",
    "noir": "noir",
    "小红帽": "red-hood",
    "红帽": "red-hood",
    "red-hood": "red-hood",
    "红莲暗影": "scarlet-black-shadow",
    "黑莲": "scarlet-black-shadow",
    "神罚": "modernia",
    "modernia": "modernia",
    "爱丽丝": "alice",
    "alice": "alice",
    "麦斯威尔": "maxwell",
    "maxwell": "maxwell",
    "诺伊斯": "noise",
    "noise": "noise",
    "佩珀": "pepper",
    "pepper": "pepper",
    "艾米莉亚": "emilia",
    "emilia": "emilia",
    "灰姑娘": "cinderella",
    "cinderella": "cinderella",
    "贝斯蒂": "bvesti",
    "海伦": "helen",
    "海伦珍藏": "helen-treasure",
    "普丽瓦蒂": "privaty",
    "privaty": "privaty",
    "普丽瓦蒂不洁": "privaty-unkind-maid",
    "波莉": "polly",
    "polly": "polly",
    "毒蛇": "viper",
    "viper": "viper",
    "梅登": "maiden",
    "maiden": "maiden",
    "梅登冰": "maiden-ice-rose",
    "安妮": "anne-miracle-fairy",
    "圣安妮": "anne-miracle-fairy",
    "露德米拉": "ludmilla",
    "ludmilla": "ludmilla",
    "红莲暗影": "scarlet-black-shadow",
    "尼罗": "nero",
    "nero": "尼罗",
    "马斯特": "mast",
    "mast": "mast",
    "桃乐丝": "dorothy",
    "dorothy": "dorothy",
    "丽塔": "litter",
    "litter": "litter",
    "艾可希雅": "exia",
    "exia": "exia",
    "朵拉": "dolla",
    "dolla": "dolla",
    "玛纳": "mana",
    "mana": "mana",
    "莫兰": "moran",
    "moran": "moran",
    "鲁玛尼": "rumani",
    "rumani": "rumani",
    "拉普拉斯": "laplace",
    "laplace": "laplace",
    "德雷克": "drake",
    "drake": "drake",
    "2B": "2b",
    "A2": "a2",
    "帕斯卡": "pascal",
    "pascal": "pascal",
    "枫": "sakura",
    "sakura": "sakura",
    "迪塞尔": "diesel",
    "diesel": "diesel",
    "玛律恰那": "marciana",
    "marciana": "marciana",
    "艾玛": "emma",
    "emma": "emma",
    "可可": "cocoa",
    "cocoa": "cocoa",
    "尼恩": "neon",
    "neon": "neon",
    "尼恩珍藏": "neon-treasure",
    "米哈拉": "mihara",
    "mihara": "mihara",
    "尤妮": "yuni",
    "yuni": "yuni",
    "米卡": "mica",
    "mica": "mica",
    "贝尔塔": "belorta",
    "belorta": "belorta",
    "梅里克": "mercy",
    "mercy": "mercy",
    "莱伊": "rei",
    "rei": "rei",
    "阿妮斯尼恩双人": "anis-neon",
    "索达": "soda",
    "soda": "soda",
    "索达兔": "soda-bunny",
    "坎西": "quency",
    "quency": "quency",
    "坎西逃": "quency-escape-queen",
}

PRYDWEN_BASE = "https://img.prydwen.gg/nikke/characters"


def _try_download_avatar(char_name, avatar_id):
    """尝试从 Prydwen 下载角色头像"""
    urls = [
        f"{PRYDWEN_BASE}/icon_{avatar_id}.png",
        f"{PRYDWEN_BASE}/avatar_{avatar_id}.png",
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200 and len(resp.content) > 1000:
                safe_name = char_name.replace(" ", "_")
                path = AVATAR_DIR / f"{safe_name}.png"
                with open(path, "wb") as f:
                    f.write(resp.content)
                return f"/avatars/{safe_name}.png"
        except requests.RequestException:
            continue
    return None


def get_avatar_url(char_name):
    # 先检查本地
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", char_name.replace(" ", "_"))
    local = AVATAR_DIR / f"{safe}.png"
    if local.exists():
        return f"/avatars/{safe}.png"

    # 查映射表下载
    key = char_name.lower().strip()
    avatar_id = AVATAR_LOOKUP.get(char_name) or AVATAR_LOOKUP.get(key)
    if avatar_id:
        url = _try_download_avatar(char_name, avatar_id)
        if url:
            return url
    return None


# ──────────────────────────────────────
# Flask 应用
# ──────────────────────────────────────

app = Flask(__name__, static_folder="static", static_url_path="")


# ── 静态页面 ──
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/default-avatar.png")
def serve_default_avatar():
    """默認頭像（無頭像角色備用）"""
    path = STATIC_DIR / "default-avatar.png" if (STATIC_DIR := Path(app.static_folder)).exists() \
        else AVATAR_DIR / "default.png"
    if path.exists():
        return send_file(str(path), mimetype="image/png")
    # 兜底：生成一個簡單的 SVG
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="80" height="80" fill="#7b61ff"/><text x="40" y="48" text-anchor="middle" font-size="32" fill="white" font-family="sans-serif">N</text></svg>'
    return Response(svg, mimetype="image/svg+xml")


@app.route("/avatars/<name>")
def serve_avatar(name):
    return send_from_directory(AVATAR_DIR, name)


# ── 角色 API ──

@app.route("/api/characters", methods=["GET"])
def api_list_characters():
    chars = load_characters()
    # 筛选参数
    cls = request.args.get("class")
    mfg = request.args.get("manufacturer")
    wpn = request.args.get("weapon")
    code = request.args.get("code")
    burst = request.args.get("burst")
    starred = request.args.get("starred")
    q = request.args.get("q", "").strip().lower()

    if cls:
        chars = [c for c in chars if c.get("class") == cls]
    if mfg:
        chars = [c for c in chars if c.get("manufacturer") == mfg]
    if wpn:
        chars = [c for c in chars if c.get("weapon") == wpn]
    if code:
        chars = [c for c in chars if c.get("code") == code]
    if burst:
        chars = [c for c in chars if c.get("burst") == burst or c.get("burst") == "全"]
    if starred:
        chars = [c for c in chars if c.get("starred")]
    if q:
        chars = [c for c in chars if _matches_query(c.get("name", ""), q) or _matches_query(c.get("alias", "") or "", q)]

    return jsonify(chars)


@app.route("/api/characters", methods=["POST"])
def api_add_character():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    alias = data.get("alias", "").strip() or None
    if not name:
        return jsonify({"error": "角色名不能为空"}), 400

    duplicate = _find_duplicate_character(name, alias)
    if duplicate:
        return jsonify({"error": "角色名或别名已存在"}), 409

    chars = load_characters()
    char = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "alias": alias,
        "class": data.get("class", ""),
        "manufacturer": data.get("manufacturer", ""),
        "weapon": data.get("weapon", ""),
        "code": data.get("code", ""),
        "burst": data.get("burst", ""),
        "avatar_url": data.get("avatar_url") or None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    chars.append(char)
    save_characters(chars)
    return jsonify(char), 201


@app.route("/api/characters/<char_id>", methods=["PUT"])
def api_update_character(char_id):
    data = request.get_json() or {}
    chars = load_characters()
    name = data.get("name")
    alias = data.get("alias") if "alias" in data else None

    if name:
        name = name.strip()
    for c in chars:
        if c["id"] == char_id:
            new_name = name or c["name"]
            new_alias = alias.strip() if alias is not None else c.get("alias")
            if new_alias == "":
                new_alias = None

            duplicate = _find_duplicate_character(new_name, new_alias, exclude_id=char_id)
            if duplicate:
                return jsonify({"error": "角色名或别名已存在"}), 409

            c["name"] = new_name
            if alias is not None:
                c["alias"] = new_alias
            c["class"] = data.get("class", c.get("class", ""))
            c["manufacturer"] = data.get("manufacturer", c.get("manufacturer", ""))
            c["weapon"] = data.get("weapon", c.get("weapon", ""))
            c["code"] = data.get("code", c.get("code", ""))
            c["burst"] = data.get("burst", c.get("burst", ""))
            c["avatar_url"] = data.get("avatar_url", c.get("avatar_url"))
            save_characters(chars)
            return jsonify(c)
    return jsonify({"error": "角色不存在"}), 404


@app.route("/api/characters/<char_id>", methods=["DELETE"])
def api_delete_character(char_id):
    chars = load_characters()
    new_chars = [c for c in chars if c["id"] != char_id]
    if len(new_chars) == len(chars):
        return jsonify({"error": "角色不存在"}), 404
    save_characters(new_chars)
    return jsonify({"status": "ok"})


@app.route("/api/characters/<char_id>/avatar", methods=["POST"])
def api_upload_avatar(char_id):
    chars = load_characters()
    for c in chars:
        if c["id"] == char_id:
            if "file" not in request.files:
                return jsonify({"error": "没有上传文件"}), 400
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "文件为空"}), 400
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "png"
            if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
                return jsonify({"error": "不支持的图片格式"}), 400
            safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{char_id}_{c['name']}.{ext}")
            filepath = AVATAR_DIR / safe_name
            file.save(filepath)
            c["avatar_url"] = f"/avatars/{safe_name}"
            save_characters(chars)
            return jsonify(c)
    return jsonify({"error": "角色不存在"}), 404


@app.route("/api/characters/sync-avatars", methods=["POST"])
def api_sync_avatars():
    """手動從 seed 文件同步所有角色的 avatar_url"""
    seed_file = _find_seed_file()
    if not seed_file:
        return jsonify({"error": "找不到角色種子文件"}), 500
    with open(str(seed_file), "r", encoding="utf-8") as f:
        seed_data = json.load(f)
    seed_map = {}
    for c in seed_data:
        seed_map[c["name"]] = c.get("avatar_url") or None
        if c.get("alias"):
            seed_map[c["alias"]] = c.get("avatar_url") or None

    chars = load_characters()
    updated = 0
    for c in chars:
        url = seed_map.get(c["name"]) or seed_map.get(c.get("alias", ""))
        if url and c.get("avatar_url") != url:
            c["avatar_url"] = url
            updated += 1
    if updated:
        save_characters(chars)
    return jsonify({"status": "ok", "updated": updated, "total": len(chars)})


@app.route("/api/characters/<char_id>/toggle-star", methods=["POST"])
def api_toggle_star(char_id):
    """切换角色标⭐状态"""
    chars = load_characters()
    for c in chars:
        if c["id"] == char_id:
            c["starred"] = not c.get("starred", False)
            save_characters(chars)
            return jsonify({"status": "ok", "starred": c["starred"]})
    return jsonify({"error": "角色不存在"}), 404


# ── 战绩 API ──

@app.route("/api/records", methods=["GET"])
def api_list_records():
    records = load_records()
    # 参数过滤
    limit = request.args.get("limit", type=int, default=0)
    mode = request.args.get("mode")
    result = request.args.get("result")
    opponent = request.args.get("opponent")
    q = request.args.get("q", "").strip().lower()
    q_scope = request.args.get("q_scope", "all")
    q_logic = request.args.get("q_logic", "or")
    if q_scope not in ("all", "my", "opp", "opponent"):
        q_scope = "all"
    if q_logic not in ("or", "and", "not"):
        q_logic = "or"

    if mode:
        records = [r for r in records if r["mode"] == mode]
    if result:
        records = [r for r in records if r["result"] == result]
    if opponent:
        records = [r for r in records if opponent.lower() in r.get("opponent", "").lower()]
    if q:
        tokens = [t for t in re.split(r"[\s,，、]+", q) if t]
        if not tokens:
            tokens = [q]

        def record_texts(record, scope):
            texts = []
            if scope in ("all", "opponent"):
                texts.append(record.get("opponent", ""))
            if scope in ("all", "my"):
                texts.extend(record.get("my_team", []))
            if scope in ("all", "opp"):
                texts.extend(record.get("opp_team", []))
            return texts

        def matches_token(record, token):
            return any(_matches_query(text, token) for text in record_texts(record, q_scope))

        def matches_record(record):
            hits = [matches_token(record, token) for token in tokens]
            if q_logic == "and":
                return all(hits)
            if q_logic == "not":
                return not any(hits)
            return any(hits)

        records = [r for r in records if matches_record(r)]

    records.sort(key=lambda r: r["timestamp"], reverse=True)
    if limit and limit > 0:
        records = records[:limit]
    return jsonify(records)


@app.route("/api/records", methods=["POST"])
def api_add_record():
    data = request.get_json() or {}
    my_team = data.get("my_team", [])
    opp_team = data.get("opp_team", [])

    if not isinstance(my_team, list) or len(my_team) != 5:
        return jsonify({"error": "我方需要恰好 5 个角色"}), 400
    if not isinstance(opp_team, list) or len(opp_team) != 5:
        return jsonify({"error": "对方需要恰好 5 个角色"}), 400

    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": data.get("mode", "attack"),
        "result": data.get("result", "win"),
        "opponent": data.get("opponent", "").strip() or "未知",
        "my_team": resolve_team_names(my_team),
        "opp_team": resolve_team_names(opp_team),
        "notes": data.get("notes", "").strip() or "",
    }

    records = load_records()
    records.append(record)
    save_records(records)
    return jsonify(record), 201


@app.route("/api/records/<record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    records = load_records()
    new_records = [r for r in records if r["id"] != record_id]
    if len(new_records) == len(records):
        return jsonify({"error": "记录不存在"}), 404
    save_records(new_records)
    return jsonify({"status": "ok"})


# ── 统计 API ──

@app.route("/api/stats/overview")
def api_stats_overview():
    records = load_records()
    total = len(records)
    if total == 0:
        return jsonify({"total": 0, "wins": 0, "losses": 0, "win_rate": 0})

    wins = sum(1 for r in records if r["result"] == "win")
    losses = total - wins

    return jsonify({
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / total * 100, 1),
    })


@app.route("/api/stats/by-unit")
def api_stats_by_unit():
    records = load_records()
    unit_stats = {}

    for r in records:
        for name in r["my_team"]:
            if name not in unit_stats:
                unit_stats[name] = {"appearances": 0, "wins": 0}
            unit_stats[name]["appearances"] += 1
            if r["result"] == "win":
                unit_stats[name]["wins"] += 1

    result = []
    for name, stats in sorted(unit_stats.items(), key=lambda x: -x[1]["appearances"]):
        result.append({
            "name": name,
            "appearances": stats["appearances"],
            "wins": stats["wins"],
            "win_rate": round(stats["wins"] / stats["appearances"] * 100, 1),
        })
    return jsonify(result)


@app.route("/api/stats/by-team")
def api_stats_by_team():
    records = load_records()
    team_stats = {}

    for r in records:
        key = ",".join(sorted(set(r["my_team"])))
        if key not in team_stats:
            team_stats[key] = {
                "team": sorted(r["my_team"]),
                "appearances": 0,
                "wins": 0,
            }
        team_stats[key]["appearances"] += 1
        if r["result"] == "win":
            team_stats[key]["wins"] += 1

    result = []
    for key, stats in sorted(team_stats.items(), key=lambda x: -x[1]["appearances"]):
        result.append({
            "team": stats["team"],
            "appearances": stats["appearances"],
            "wins": stats["wins"],
            "win_rate": round(stats["wins"] / stats["appearances"] * 100, 1),
        })
    return jsonify(result)


@app.route("/api/stats/by-opponent")
def api_stats_by_opponent():
    records = load_records()
    opp_stats = {}

    for r in records:
        name = r.get("opponent", "未知")
        if name not in opp_stats:
            opp_stats[name] = {"appearances": 0, "wins": 0, "lost_teams": []}
        opp_stats[name]["appearances"] += 1
        if r["result"] == "win":
            opp_stats[name]["wins"] += 1

    result = []
    for name, stats in sorted(opp_stats.items(), key=lambda x: -x[1]["appearances"]):
        result.append({
            "opponent": name,
            "appearances": stats["appearances"],
            "wins": stats["wins"],
            "win_rate": round(stats["wins"] / stats["appearances"] * 100, 1),
        })
    return jsonify(result)


# ── 角色名补全 ──

@app.route("/api/search/characters")
def api_search_characters():
    q = request.args.get("q", "").strip().lower()
    chars = load_characters()
    results = [c for c in chars if _matches_query(c.get("name", ""), q) or _matches_query(c.get("alias", "") or "", q)]
    return jsonify(results)


# ── 筛选枚举 ──

@app.route("/api/enums")
def api_enums():
    return jsonify({
        "classes": CHAR_CLASSES,
        "manufacturers": CHAR_MANUFACTURERS,
        "weapons": CHAR_WEAPONS,
        "codes": CHAR_CODES,
        "bursts": CHAR_BURSTS,
    })


# ── 重新導入角色（從 nikke_characters.json）──

@app.route("/api/characters/seed", methods=["POST"])
def api_seed_characters():
    """從 nikke_characters.json 重新導入角色數據（不清除已有記錄）"""
    chars = load_characters()
    if chars:
        return jsonify({"status": "ok", "message": "角色數據已存在，無需導入", "count": len(chars)})

    seed_candidates = [
        BASE_DIR / "data" / "nikke_characters.json",
    ]
    if getattr(_sys, '_MEIPASS', None):
        seed_candidates.append(Path(_sys._MEIPASS) / "data" / "nikke_characters.json")

    for seed_file in seed_candidates:
        if seed_file.exists():
            import shutil
            # 讀取並補 id 字段（源數據可能缺 id）
            with open(str(seed_file), "r", encoding="utf-8") as f:
                raw = json.load(f)
            for c in raw:
                if "id" not in c or not c["id"]:
                    c["id"] = str(uuid.uuid4())[:8]
            save_characters(raw)
            return jsonify({"status": "ok", "message": f"成功導入 {len(raw)} 個角色", "count": len(raw)})

    return jsonify({"error": "找不到 nikke_characters.json 數據文件"}), 404


# ── 批量导出 ──

@app.route("/api/records/export", methods=["GET"])
def api_export_records():
    records = load_records()
    fmt = request.args.get("format", "json")
    if fmt == "csv":
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["时间", "模式", "结果", "对手", "我方队伍", "对方队伍", "备注"])
        for r in records:
            writer.writerow([
                r["timestamp"],
                "进攻" if r["mode"] == "attack" else "防守",
                "胜利" if r["result"] == "win" else "失败",
                r.get("opponent", ""),
                "/".join(r["my_team"]),
                "/".join(r["opp_team"]),
                r.get("notes", ""),
            ])
        csv_data = output.getvalue()
        return Response(
            csv_data,
            mimetype="text/csv; charset=utf-8-sig",
            headers={"Content-Disposition": "attachment; filename=nikke_pvp_records.csv"},
        )
    return jsonify(records)


# ── 批量导入 ──

@app.route("/api/records/import", methods=["POST"])
def api_import_records():
    if "file" not in request.files:
        return jsonify({"error": "没有上传文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "文件为空"}), 400
    try:
        content = file.read().decode("utf-8")
        imported = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return jsonify({"error": f"JSON 解析失败: {e}"}), 400

    if not isinstance(imported, list):
        return jsonify({"error": "需要 JSON 数组格式"}), 400

    records = load_records()
    existing_ids = {r["id"] for r in records}
    added = 0
    for item in imported:
        # 自动补全缺失字段
        if "my_team" not in item or "opp_team" not in item:
            continue
        if not isinstance(item.get("my_team"), list) or not isinstance(item.get("opp_team"), list):
            continue
        if len(item.get("my_team", [])) != 5 or len(item.get("opp_team", [])) != 5:
            continue
        rid = item.get("id", str(uuid.uuid4())[:8])
        if rid in existing_ids:
            continue
        record = {
            "id": rid,
            "timestamp": item.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "mode": item.get("mode", "attack"),
            "result": item.get("result", "win"),
            "opponent": item.get("opponent", "未知"),
            "my_team": item.get("my_team", []),
            "opp_team": item.get("opp_team", []),
            "notes": item.get("notes", ""),
        }
        records.append(record)
        existing_ids.add(rid)
        added += 1

    save_records(records)
    return jsonify({"status": "ok", "imported": added, "total": len(records)})


# ── 端口侦测 ──
def _find_free_port(start):
    """从 start 开始递增查找可用端口"""
    import socket
    for port in range(start, start + 20):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.bind(("0.0.0.0", port))
            s.close()
            return port
        except OSError:
            continue
    return None

# ── 系统托盘 ──
def _run_tray(port):
    """在 Windows 系统托盘运行图标"""
    try:
        from PIL import Image, ImageDraw
        import pystray

        # 生成一个 32x32 的图标：青色圆底 + 白色 "P" 字
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([1, 1, 30, 30], fill=(0, 212, 255, 255))
        draw.text((8, 5), "P", fill=(0, 0, 0, 255))

        def on_open():
            import webbrowser
            webbrowser.open(f"http://localhost:{port}")

        def on_exit():
            # 先强行退出，Flask 主线程随之结束
            import os as _os
            _os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("打开浏览器 (Open Browser)", on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出 (Exit)", on_exit),
        )

        icon = pystray.Icon("nikke-pvp", img, "NIKKE PVP Tracker", menu)
        icon.run()
    except Exception:
        # 托盘启动失败不阻塞主流程
        pass


# ── 全局错误处理 ──
@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    print(f"[ERROR] {e}", file=_sys.stderr)
    traceback.print_exc()
    return jsonify({"error": str(e) or "Internal Server Error"}), 500


# ── 启动 ──
if __name__ == "__main__":
    try:
        # 数据自动备份
        _data_dir = Path(str(CHARACTERS_FILE)).parent
        _backup_dir = _data_dir / "backup"
        _backup_dir.mkdir(exist_ok=True)
        _ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        _dest = _backup_dir / f"backup_{_ts}"
        _dest.mkdir(exist_ok=True)
        for _f in _data_dir.glob("*.json"):
            if _f.is_file():
                import shutil
                shutil.copy2(str(_f), str(_dest / _f.name))
        # 清理旧备份，保留最近 7 个
        _all_backups = sorted([d for d in _backup_dir.iterdir() if d.is_dir()])
        while len(_all_backups) > 7:
            _old = _all_backups.pop(0)
            import shutil
            shutil.rmtree(str(_old))

        import webbrowser
        _want_port = int(os.environ.get("PORT", 5000))
        port = _find_free_port(_want_port)
        if port is None:
            _sys.exit(1)

        # 在 Windows 上自动打开浏览器 + 启动托盘
        if _sys.platform == "win32":
            webbrowser.open(f"http://localhost:{port}")
            import threading
            threading.Thread(target=_run_tray, args=(port,), daemon=True).start()

        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as _e:
        if _sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, str(_e),
                    "NIKKE PVP Tracker - 启动失败", 0x10)
            except Exception:
                pass
        raise
