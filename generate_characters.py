#!/usr/bin/env python3
"""
Generate characters.json from blablalink data.
- Names + rarity from blablalink (SSR/SR by 2-gold-stars)
- Other fields keep existing data, override only when blablalink has values
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

parser = argparse.ArgumentParser(description="Generate characters.json from blablalink HTML data")
parser.add_argument("html_file", nargs="?", help="Source HTML/MD file containing character cards")
parser.add_argument("--characters-file", default=BASE_DIR / "data/characters.json", help="Path to existing characters.json")
args = parser.parse_args()

if args.html_file:
    html_path = Path(args.html_file)
else:
    candidates = list(BASE_DIR.glob("*.md"))
    if len(candidates) == 1:
        html_path = candidates[0]
    else:
        raise SystemExit("请提供包含 blablalink 数据的 HTML/MD 文件路径。")

if not html_path.exists():
    raise SystemExit(f"文件不存在: {html_path}")

characters_file = Path(args.characters_file)
if not characters_file.exists():
    raise SystemExit(f"找不到 characters.json: {characters_file}")

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(characters_file, 'r', encoding='utf-8') as f:
    existing = json.load(f)

cards = re.findall(
    r'<div[^>]*data-cname="(?:all-item|player-item)"[^>]*>.*?</div>\s*</div>',
    content, re.DOTALL
)

# Build existing lookup
existing_map = {c['name']: c for c in existing}

# Known data for new characters
NEW_CHAR_DATA = {
    'iDoll花': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B1'},
    'iDoll太陽': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'MG', 'code': '铁甲', 'burst': 'B3'},
    'iDoll海': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '水冷', 'burst': 'B1'},
    '士兵F.A.': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B2'},
    '士兵E.G.': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B3'},
    '士兵O.W.': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '燃烧', 'burst': 'B1'},
    '產品08': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '燃烧', 'burst': 'B1'},
    '產品12': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'MG', 'code': '燃烧', 'burst': 'B3'},
    '產品23': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B2'},
}

CODE_MAP = {
    'fire': '燃烧', 'water': '水冷', 'wind': '风压',
    'electric': '电击', 'iron': '铁甲',
}

WEAPON_MAP = {
    'sniper_rifle': 'SR', 'ar': 'AR', 'smg': 'SMG',
    'sg': 'SG', 'mg': 'MG', 'rl': 'RL',
}

BURST_MAP = {'1': 'B1', '2': 'B2', '3': 'B3'}

JOB_MAP = {'attacker': '火力', 'defender': '防御', 'supporter': '支援'}

MANUF_MAP = {
    'elysion': '极乐净土', 'missilis': '米西利斯', 'tetra': '泰特拉',
    'pilgrim': '朝圣者', 'abnormal': '反常',
}

new_characters = []
for c in cards:
    # Extract name
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
    name = name.strip()

    # Rarity from stars (2 gold = SR)
    stars = len(re.findall(r'icon-nikke-star-gold', c))
    bl_rarity = 'SR' if stars == 2 else 'SSR'

    # Get values from blablalink (may be incomplete)
    code_m = re.search(r'icon-code-([^"]+)\.png', c)
    bl_code = CODE_MAP.get(code_m.group(1), '') if code_m else ''
    weapon_m = re.search(r'icon-weapon-([^"]+)\.png', c)
    bl_weapon = WEAPON_MAP.get(weapon_m.group(1), '') if weapon_m else ''
    burst_m = re.search(r'icon-burst-(\d+)\.png', c)
    bl_burst = BURST_MAP.get(burst_m.group(1), '') if burst_m else ''
    job_m = re.search(r'nikke-job-([^"]+)--', c)
    bl_job = JOB_MAP.get(job_m.group(1), '') if job_m else ''
    manuf_m = re.search(r'icon-manufacturer-([^"]+)--', c)
    bl_manuf = MANUF_MAP.get(manuf_m.group(1), '') if manuf_m else ''

    # Start from existing data if available
    if name in existing_map:
        ex = existing_map[name]
        ch = {
            'name': name,
            'class': bl_job if bl_job else ex.get('class', ''),
            'manufacturer': bl_manuf if bl_manuf else ex.get('manufacturer', ''),
            'weapon': bl_weapon if bl_weapon else ex.get('weapon', ''),
            'code': bl_code if bl_code else ex.get('code', ''),
            'burst': bl_burst if bl_burst else ex.get('burst', ''),
            'rarity': bl_rarity,
            'avatar_url': ex.get('avatar_url', ''),
            'id': ex.get('id', ''),
            'alias': ex.get('alias'),
        }
    elif name in NEW_CHAR_DATA:
        nd = NEW_CHAR_DATA[name]
        _id = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
        ch = {
            'name': name,
            'class': bl_job if bl_job else nd['class'],
            'manufacturer': bl_manuf if bl_manuf else nd['manufacturer'],
            'weapon': bl_weapon if bl_weapon else nd['weapon'],
            'code': bl_code if bl_code else nd['code'],
            'burst': bl_burst if bl_burst else nd['burst'],
            'rarity': bl_rarity,
            'avatar_url': f'/avatars/{name}.webp',
            'id': _id,
            'alias': None,
        }
    else:
        _id = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
        ch = {
            'name': name,
            'class': bl_job,
            'manufacturer': bl_manuf,
            'weapon': bl_weapon,
            'code': bl_code,
            'burst': bl_burst,
            'rarity': bl_rarity,
            'avatar_url': f'/avatars/{name}.webp',
            'id': _id,
            'alias': None,
        }

    new_characters.append(ch)

# Sort: SSR first, then SR, then alphabetically
new_characters.sort(key=lambda c: (0 if c['rarity'] == 'SSR' else 1, c['name']))

# Write
with open('data/characters.json', 'w', encoding='utf-8') as f:
    json.dump(new_characters, f, ensure_ascii=False, indent=2)

ssr = sum(1 for c in new_characters if c['rarity'] == 'SSR')
sr = sum(1 for c in new_characters if c['rarity'] == 'SR')
print(f"Written: {len(new_characters)} characters ({ssr} SSR, {sr} SR)")

old_names = {c['name'] for c in existing}
new_names = {c['name'] for c in new_characters}
added = new_names - old_names
removed = old_names - new_names
print(f"Added: {len(added)}, Removed: {len(removed)}")
for n in sorted(added):
    print(f'  + {n}')
for n in sorted(removed):
    print(f'  - {n}')

# Print meaningful changes (rarity or class changes)
print("\n=== RARITY CHANGES ===")
for n in sorted(new_names & old_names):
    old_r = existing_map[n].get('rarity', '')
    new_r = [c for c in new_characters if c['name'] == n][0]['rarity']
    if old_r != new_r:
        print(f'  {n}: {old_r}->{new_r}')
