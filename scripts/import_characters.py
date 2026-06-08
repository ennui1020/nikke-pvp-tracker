#!/usr/bin/env python3
"""
将爬取的角色数据导入 NIKKE PVP Tracker
用法:
  python scripts/import_characters.py
  python scripts/import_characters.py --url http://localhost:5000
"""

import json
import sys
import time
from pathlib import Path

import requests

BASE_URL = "http://localhost:5000"
DATA_FILE = Path(__file__).parent.parent / "data" / "nikke_characters.json"


def main():
    url = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else BASE_URL

    if not DATA_FILE.exists():
        print(f"⚠️  数据文件不存在: {DATA_FILE}")
        print("   先运行: python scripts/scrape_characters.py")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        characters = json.load(f)

    print(f"共 {len(characters)} 个角色，正在导入 {url} ...")
    success = 0
    skipped = 0
    errors = []

    for c in characters:
        payload = {
            "name": c["name"],
            "alias": c.get("alias") or c.get("name_tw"),
            "class": c.get("class", ""),
            "manufacturer": c.get("manufacturer", ""),
            "weapon": c.get("weapon", ""),
            "code": c.get("code", ""),
            "burst": c.get("burst", ""),
            "avatar_url": None,
        }
        try:
            resp = requests.post(f"{url}/api/characters", json=payload, timeout=5)
            if resp.status_code == 201:
                success += 1
            elif resp.status_code == 409:
                skipped += 1
            else:
                errors.append(f"{c['name']}: {resp.status_code} {resp.text}")
        except requests.RequestException as e:
            errors.append(f"{c['name']}: {e}")

        time.sleep(0.05)  # 节流

    print(f"\n✅ 导入完成")
    print(f"   新增: {success}")
    print(f"   跳过（已存在）: {skipped}")
    if errors:
        print(f"   错误: {len(errors)}")
        for e in errors[:5]:
            print(f"     {e}")


if __name__ == "__main__":
    main()
