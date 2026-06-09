#!/usr/bin/env python3
import re, json

with open('/root/.hermes/cache/documents/doc_52059f6bd2a4_1.md', 'r') as f:
    content = f.read()

with open('data/characters.json', 'r') as f:
    existing = json.load(f)

cards = re.findall(
    r'<div[^>]*data-cname="(?:all-item|player-item)"[^>]*>.*?</div>\s*</div>',
    content, re.DOTALL
)

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

characters = []
for c in cards:
    code_m = re.search(r'icon-code-([^"]+)\.png', c)
    code = CODE_MAP.get(code_m.group(1), 'N/A') if code_m else 'N/A'

    weapon_m = re.search(r'icon-weapon-([^"]+)\.png', c)
    weapon = WEAPON_MAP.get(weapon_m.group(1), 'N/A') if weapon_m else 'N/A'

    burst_m = re.search(r'icon-burst-(\d+)\.png', c)
    burst = BURST_MAP.get(burst_m.group(1), 'N/A') if burst_m else 'N/A'

    job_m = re.search(r'nikke-job-([^"]+)--', c)
    job = JOB_MAP.get(job_m.group(1), 'N/A') if job_m else 'N/A'

    manuf_m = re.search(r'icon-manufacturer-([^"]+)--', c)
    manuf = MANUF_MAP.get(manuf_m.group(1), '') if manuf_m else ''

    stars = len(re.findall(r'icon-nikke-star-gold', c))

    # name
    name = None
    m = re.search(r'class="name[^"]*"[^>]*>\s*<span[^>]*>\s*([^<>\n]+?)\s*</span>', c)
    if m:
        name = m.group(1).strip()
    if not name:
        m = re.search(r'text-stroke1[^>]*>([^<]+)</div>', c)
        if m:
            name = m.group(1).strip()
    name = name or 'UNKNOWN'

    rarity = 'SR' if stars == 2 else 'SSR'

    characters.append({
        'name': name,
        'code': code,
        'weapon': weapon,
        'burst': burst,
        'class': job,
        'manufacturer': manuf,
        'rarity': rarity,
    })

# Build lookup of blablalink data by name
bl_map = {c['name']: c for c in characters}

# Match with existing data to find name differences
existing_map = {c['name']: c for c in existing}

# Find characters whose names differ between our data and blablalink
# Our data has some names that were likely wrong.
# Let's compare by looking for similar but different names

# All existing names
print("=== NAME DIFFERENCES ===")
for ex in existing:
    en = ex['name']
    if en not in bl_map:
        # Check for similar names
        found = None
        # Simple fuzzy: check if en contains bl name or vice versa
        for bn in bl_map:
            # Check for case where one is a substring of other, or collon variants
            if en.replace(':', '：') == bn or en.replace('：', ':') == bn:
                found = bn
                break
            # Simple substring check
            if en in bn or bn in en:
                if len(en) >= 2 and len(bn) >= 2:
                    found = bn
                    break
        if found:
            print(f'  {en:20s} -> {found:20s} (similar)')
        else:
            print(f'  {en:20s} -> MISSING from blablalink')
    else:
        # Check if fields differ
        bl = bl_map[en]
        diffs = []
        for field in ['code', 'weapon', 'burst', 'class']:
            if ex.get(field) != bl[field] and bl[field] != 'N/A':
                diffs.append(f'{field}: {ex.get(field)}->{bl[field]}')
        if diffs:
            print(f'  {en:20s} diff: {", ".join(diffs)}')

# Also check new names
print("\n=== NEW CHARACTERS ===")
for bn, bl in bl_map.items():
    if bn not in existing_map:
        print(f'  + {bn:20s} {bl["rarity"]} {bl["class"]}')

# Check manufacturer for all characters we can identify
# For player-owned cards, we don't have manufacturer in the HTML
# Let's use existing data's manufacturer when name matches
print("\n=== MANUFACTURER CHECK ===")
for ch in characters:
    if not ch['manufacturer']:
        # Try to find in existing data by name
        ex = existing_map.get(ch['name'])
        if ex:
            ch['manufacturer'] = ex.get('manufacturer', 'N/A')

# Count what we still need
missing_manuf = [c for c in characters if not c['manufacturer']]
print(f"Characters missing manufacturer: {len(missing_manuf)}")
for c in missing_manuf[:10]:
    print(f'  - {c["name"]}')
if len(missing_manuf) > 10:
    print(f'  ... and {len(missing_manuf)-10} more')
