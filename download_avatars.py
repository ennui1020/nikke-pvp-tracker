#!/usr/bin/env python3
"""Download avatars in batches from blablalink CDN."""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent

parser = argparse.ArgumentParser(description="Download avatars from blablalink HTML data")
parser.add_argument("html_file", nargs="?", help="Source HTML/MD file containing avatar cards")
parser.add_argument("--avatars-dir", default=BASE_DIR / "avatars", help="Output avatars directory")
parser.add_argument("--characters-file", default=BASE_DIR / "data/characters.json", help="Path to data/characters.json")
args = parser.parse_args()

if args.html_file:
    HTML_FILE = Path(args.html_file)
else:
    raise SystemExit("请提供包含 blablalink 数据的 HTML/MD 文件路径。")

if not HTML_FILE.exists():
    raise SystemExit(f"文件不存在: {HTML_FILE}")

AVATARS_DIR = Path(args.avatars_dir)
CHARACTERS_FILE = Path(args.characters_file)
AVATARS_DIR.mkdir(parents=True, exist_ok=True)

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

cards = re.findall(
    r'<div[^>]*data-cname="(?:all-item|player-item)"[^>]*>.*?</div>\s*</div>',
    content, re.DOTALL
)

avatar_map = {}
for c in cards:
    img_m = re.search(r'src="(https://sg-tools-cdn\.blablalink\.com[^"]+\.webp)"', c)
    if not img_m:
        continue
    img_url = img_m.group(1)
    name = None
    m = re.search(r'class="name[^"]*"[^>]*>\s*<span[^>]*>\s*([^<>\n]+?)\s*</span>', c)
    if m:
        name = m.group(1).strip()
    if not name:
        m = re.search(r'text-stroke1[^>]*>([^<]+)</div>', c)
        if m:
            name = m.group(1).strip()
    if not name:
        continue
    avatar_map[name] = img_url

# Check existing
existing = set()
for f in os.listdir(AVATARS_DIR):
    name_no_ext = os.path.splitext(f)[0]
    existing.add(name_no_ext)

# Only download missing
to_download = {k: v for k, v in avatar_map.items() if k not in existing}
print(f"Total: {len(avatar_map)}, Existing: {len(existing)}, To download: {len(to_download)}")

if not to_download:
    print("All avatars already exist!")
    sys.exit(0)

os.makedirs(AVATARS_DIR, exist_ok=True)

def download_one(item):
    name, url = item
    ext = 'png' if name in ('2B', 'A2') else 'webp'
    filepath = os.path.join(AVATARS_DIR, f"{name}.{ext}")
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(filepath, 'wb') as f:
                f.write(data)
        return (name, len(data), None)
    except Exception as e:
        return (name, 0, str(e))

success = 0
failed = 0
items = list(to_download.items())

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(download_one, item): item[0] for item in items}
    for future in as_completed(futures):
        name, size, err = future.result()
        if err:
            print(f"  FAIL {name}: {err}")
            failed += 1
        else:
            print(f"  OK   {name} ({size} bytes)")
            success += 1

print(f"\nDone: {success} new downloaded, {failed} failed")

# Update characters.json
if not CHARACTERS_FILE.exists():
    raise SystemExit(f"找不到 characters.json: {CHARACTERS_FILE}")

with open(CHARACTERS_FILE, 'r', encoding='utf-8') as f:
    chars = json.load(f)

actual_names = set()
for f in os.listdir(AVATARS_DIR):
    if f.endswith((".webp", ".png")):
        actual_names.add(os.path.splitext(f)[0])

for ch in chars:
    name = ch['name']
    if name in actual_names:
        ext = 'png' if name in ('2B', 'A2') else 'webp'
        ch['avatar_url'] = f'/avatars/{name}.{ext}'
    else:
        ch['avatar_url'] = None

with open(CHARACTERS_FILE, 'w', encoding='utf-8') as f:
    json.dump(chars, f, ensure_ascii=False, indent=2)

av_with = sum(1 for c in chars if c.get('avatar_url'))
av_without = sum(1 for c in chars if not c.get('avatar_url'))
print(f"characters.json: {av_with} with avatar, {av_without} without")
