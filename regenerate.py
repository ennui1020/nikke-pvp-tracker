#!/usr/bin/env python3
"""Regenerate characters.json with proper field data from pre-blablalink backup."""
import json, hashlib

# Load earliest backup (has correct class/weapon/code/burst data)
with open('data/backup/backup_20260609_085118/characters.json') as f:
    old_chars = json.load(f)

# Load current (blablalink names, but empty fields)
with open('data/characters.json') as f:
    new_chars = json.load(f)

# Build old name -> data mapping
# Old data has some name variants - normalize for matching
old_map = {}
for c in old_chars:
    old_map[c['name']] = c

# Extended name mapping: old_name -> blablalink_name
# These are all the renamed characters between old data and blablalink
NAME_MAP = {
    'D:殺手妻子': 'D：殺手妻子',
    '伊萊格:BOOM與驚嚇': '伊萊格：BOOM與驚嚇',
    '克蕾兒·雷德費爾德': '克蕾兒',
    '克雷': '克雷伊',
    '吉兒·華倫泰': '吉兒',
    '坎西:逃生女王': '坎西：逃生女王',
    '安克:天真的女僕': '安克：天真的女僕',
    '安妮:奇蹟仙女': '安妮：奇蹟仙女',
    '尼恩:藍色海洋': '尼恩：藍色海洋',
    '尼恩:透視之眼': '尼恩：透視之眼',
    '布麗德:靜默軌道': '布麗德：靜默軌道',
    '式波·明日香·蘭格雷': '明日香',
    '式波·明日香·蘭格雷：WILLE': '明日香：WILLE',
    '井之上瀧奈': '瀧奈',
    '德爾塔:怪盜忍者': '德爾塔：怪盜忍者',
    '愛德:特務兔女郎': '愛德：特務兔女郎',
    '愛麗絲:仙境兔女郎': '愛麗絲：仙境兔女郎',
    '拉毗:小紅帽': '拉毗：小紅帽',
    '普麗瓦蒂:不友善的女僕': '普麗瓦蒂：不友善的女僕',
    '桃樂絲:機緣巧遇': '桃樂絲：機緣巧遇',
    '梅登:冰玫瑰': '梅登：冰玫瑰',
    '梅里:海灣女神': '梅里：海灣女神',
    '森提': '森',
    '櫻花:夏日綻放': '櫻花：夏日綻放',
    '海倫:海藍寶石': '海倫：海藍寶石',
    '白雪公主:重型武裝': '白雪公主：重型武裝',
    '真希波·真理·伊拉絲多莉雅斯': '真理',
    '米卡:雪地夥伴': '米卡：雪地夥伴',
    '米哈拉:羈絆鎖鏈': '米哈拉：羈絆鎖鏈',
    '米爾克:花漾兔女郎': '米爾克：花漾兔女郎',
    '紅蓮:暗影': '紅蓮：暗影',
    '索林:霜雪車票': '索林：霜雪車票',
    '索達:閃亮兔女郎': '索達：閃亮兔女郎',
    '綾波零': '零',
    '綾波零【暫稱】': '零（暫稱）',
    '羅珊娜:高雅海洋': '羅珊娜：高雅海洋',
    '艾瑪:戰術升級': '艾瑪：戰術升級',
    '艾達·王': '艾達',
    '芙蘿拉': '芙羅拉',
    '梅吉蘿婷:寒冬殺手': '吉蘿婷：寒冬殺手',
    '貝斯蒂:戰術升級': '貝斯蒂：戰術升級',
    '迪塞爾:冬日甜心': '迪塞爾：冬日甜心',
    '銀華:戰術升級': '銀華：戰術升級',
    '錦木千束': '千束',
    '長髮公主:純白承諾': '長髮公主：純潔恩典',
    '阿妮斯:超級巨星': '阿妮斯：超級巨星',
    '阿妮斯:閃耀夏日': '阿妮斯：閃耀夏日',
    '阿爾卡娜:命運伴侶': '阿爾卡娜：命運伴侶',
    '雷雯': '蕾雯',
    '露菲:冬日購物狂': '露菲：冬日購物狂',
    '馬斯特:浪漫的女僕': '馬斯特：浪漫的女僕',
    '魯德米拉:冬日之主': '魯德米拉：冬日之主',
    '魯瑪尼': '魯瑪妮',
    '白雪公主:純真之日': '白雪公主：純真年代',
    '鈴原櫻': '櫻',
    '芙里瑪': '阿維斯塔',
    '莫蘭': '阿爾卡娜',
    '紅胡桃': '胡桃',
    '葛城美里': '美里',
    '魯吉': '露姬',
    '諾瓦': '諾雅',
    '辛': '茨瓦伊',
    '蓓': '普莉卡',
}

# Hardcoded correct data for new characters not in backup
KNOWN_DATA = {
    '桑迪': {'class': '防御', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '铁甲', 'burst': 'B2'},
    '梅里': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'SG', 'code': '水冷', 'burst': 'B1'},
    '德爾塔': {'class': '防御', 'manufacturer': '极乐净土', 'weapon': 'AR', 'code': '风压', 'burst': 'B2'},
    'N102': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '水冷', 'burst': 'B1'},
    '帕斯卡': {'class': '支援', 'manufacturer': '反常', 'weapon': 'RL', 'code': '铁甲', 'burst': 'B1'},
    '索拉': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'RL', 'code': '风压', 'burst': 'B1'},
    '蕾貝兒': {'class': '防御', 'manufacturer': '极乐净土', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B1'},
    '白鶴': {'class': '防御', 'manufacturer': '米西利斯', 'weapon': 'SR', 'code': '水冷', 'burst': 'B2'},
    '基里': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'RL', 'code': '风压', 'burst': 'B3'},
    '諾亞爾': {'class': '火力', 'manufacturer': '泰特拉', 'weapon': 'SG', 'code': '风压', 'burst': 'B3'},
    '阿維斯塔': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'MG', 'code': '风压', 'burst': 'B1'},
    '阿爾卡娜': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '风压', 'burst': 'B2'},
    '普莉卡': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SR', 'code': '水冷', 'burst': 'B2'},
    '克雷伊': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B2'},
    '克蕾兒': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '风压', 'burst': 'B1'},
    '胡桃': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B1'},
    '百合': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B2'},
    '莫莉': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'AR', 'code': '风压', 'burst': 'B2'},
    '貝伊': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'RL', 'code': '燃烧', 'burst': 'B2'},
    '萊伊': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'SMG', 'code': '水冷', 'burst': 'B1'},
    '美里': {'class': '支援', 'manufacturer': '反常', 'weapon': 'SMG', 'code': '铁甲', 'burst': 'B1'},
    '富克旺': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'AR', 'code': '水冷', 'burst': 'B2'},
    '諾薇兒': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'SMG', 'code': '铁甲', 'burst': 'B2'},
    '吉洛': {'class': '防御', 'manufacturer': '极乐净土', 'weapon': 'MG', 'code': '燃烧', 'burst': 'B3'},
    '特蕾娜': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'RL', 'code': '水冷', 'burst': 'B2'},
    '尤莉亞': {'class': '火力', 'manufacturer': '极乐净土', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B3'},
    '特羅尼': {'class': '火力', 'manufacturer': '极乐净土', 'weapon': 'SR', 'code': '燃烧', 'burst': 'B3'},
    '普琳瑪': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'SR', 'code': '铁甲', 'burst': 'B1'},
    '朵拉': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'SR', 'code': '风压', 'burst': 'B2'},
    '可可': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SR', 'code': '燃烧', 'burst': 'B1'},
    '艾瑟兒': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SG', 'code': '风压', 'burst': 'B1'},
    '鐘鳴': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'SMG', 'code': '铁甲', 'burst': 'B2'},
    '尼羅': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'SMG', 'code': '燃烧', 'burst': 'B2'},
    '馬斯特': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'SMG', 'code': '风压', 'burst': 'B2'},
    '露姬': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'SR', 'code': '电击', 'burst': 'B1'},
    '萊昂納': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'SG', 'code': '水冷', 'burst': 'B2'},
    '艾可希雅': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'SR', 'code': '风压', 'burst': 'B1'},
    '茨瓦伊': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SG', 'code': '水冷', 'burst': 'B1'},
    '潘托姆': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '水冷', 'burst': 'B3'},
    '瑪娜': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '风压', 'burst': 'B3'},
    '尼希利斯塔': {'class': '火力', 'manufacturer': '反常', 'weapon': 'SR', 'code': '燃烧', 'burst': 'B2'},
    'A2': {'class': '火力', 'manufacturer': '反常', 'weapon': 'RL', 'code': '燃烧', 'burst': 'B3'},
    '2B': {'class': '防御', 'manufacturer': '反常', 'weapon': 'AR', 'code': '燃烧', 'burst': 'B3'},
    '瑪律恰那': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SG', 'code': '铁甲', 'burst': 'B2'},
    '莉貝雷利奧': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'SR', 'code': '风压', 'burst': 'B3'},
    '艾菲涅爾': {'class': '火力', 'manufacturer': '极乐净土', 'weapon': 'SMG', 'code': '风压', 'burst': 'B3'},
    '薇爾維特': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'SR', 'code': '铁甲', 'burst': 'B2'},
    '芙羅拉': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'MG', 'code': '风压', 'burst': 'B2'},
    '伊芙': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B3'},
    '吉兒': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '风压', 'burst': 'B3'},
    '千束': {'class': '火力', 'manufacturer': '反常', 'weapon': 'SMG', 'code': '铁甲', 'burst': 'B3'},
    '瀧奈': {'class': '支援', 'manufacturer': '反常', 'weapon': 'SR', 'code': '铁甲', 'burst': 'B2'},
    '帕瓦': {'class': '火力', 'manufacturer': '反常', 'weapon': 'RL', 'code': '燃烧', 'burst': 'B3'},
    '姬野': {'class': '支援', 'manufacturer': '反常', 'weapon': 'SR', 'code': '风压', 'burst': 'B2'},
    '真紀真': {'class': '防御', 'manufacturer': '反常', 'weapon': 'SMG', 'code': '水冷', 'burst': 'B2'},
    '拉姆': {'class': '防御', 'manufacturer': '反常', 'weapon': 'SR', 'code': '风压', 'burst': 'B1'},
    '雷姆': {'class': '支援', 'manufacturer': '反常', 'weapon': 'MG', 'code': '水冷', 'burst': 'B2'},
    '愛蜜莉雅': {'class': '火力', 'manufacturer': '反常', 'weapon': 'RL', 'code': '水冷', 'burst': 'B3'},
    '明日香': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '燃烧', 'burst': 'B3'},
    '明日香：WILLE': {'class': '火力', 'manufacturer': '反常', 'weapon': 'MG', 'code': '风压', 'burst': 'B3'},
    '真理': {'class': '支援', 'manufacturer': '反常', 'weapon': 'SR', 'code': '风压', 'burst': 'B2'},
    '零': {'class': '火力', 'manufacturer': '反常', 'weapon': 'MG', 'code': '燃烧', 'burst': 'B3'},
    '零（暫稱）': {'class': '火力', 'manufacturer': '反常', 'weapon': 'AR', 'code': '风压', 'burst': 'B3'},
    'E.H.': {'class': '火力', 'manufacturer': '极乐净土', 'weapon': 'SMG', 'code': '风压', 'burst': 'B3'},
    'K': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '电击', 'burst': 'B3'},
    'iDoll花': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B1'},
    'iDoll太陽': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'MG', 'code': '铁甲', 'burst': 'B3'},
    'iDoll海': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '水冷', 'burst': 'B1'},
    '士兵F.A.': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'AR', 'code': '铁甲', 'burst': 'B2'},
    '士兵E.G.': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B3'},
    '士兵O.W.': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '燃烧', 'burst': 'B1'},
    '產品08': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '燃烧', 'burst': 'B1'},
    '產品12': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'MG', 'code': '燃烧', 'burst': 'B3'},
    '產品23': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'SMG', 'code': '风压', 'burst': 'B2'},
    '尼夫': {'class': '火力', 'manufacturer': '米西利斯', 'weapon': 'SG', 'code': '水冷', 'burst': 'B3'},
    '米卡': {'class': '支援', 'manufacturer': '极乐净土', 'weapon': 'RL', 'code': '风压', 'burst': 'B1'},
    '貝洛塔': {'class': '火力', 'manufacturer': '泰特拉', 'weapon': 'RL', 'code': '铁甲', 'burst': 'B2'},
    '牡丹': {'class': '防御', 'manufacturer': '泰特拉', 'weapon': 'AR', 'code': '水冷', 'burst': 'B1'},
    '安克': {'class': '防御', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '风压', 'burst': 'B1'},
    '桑迪': {'class': '防御', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '铁甲', 'burst': 'B2'},
    '克勞斯特': {'class': '支援', 'manufacturer': '米西利斯', 'weapon': 'RL', 'code': '水冷', 'burst': 'B2'},
    '櫻花：夏日綻放': {'class': '火力', 'manufacturer': '泰特拉', 'weapon': 'AR', 'code': '风压', 'burst': 'B3'},
    '阿妮斯：閃耀夏日': {'class': '支援', 'manufacturer': '泰特拉', 'weapon': 'SG', 'code': '风压', 'burst': 'B1'},
}

# Build reverse map: blablalink name -> old name
rev_map = {v: k for k, v in NAME_MAP.items()}

def get_old_data(bl_name):
    """Find matching old data for a blablalink name."""
    # Direct match
    if bl_name in old_map:
        return old_map[bl_name]
    # Reverse name map
    if bl_name in rev_map:
        old_name = rev_map[bl_name]
        if old_name in old_map:
            return old_map[old_name]
    # Hardcoded known data
    if bl_name in KNOWN_DATA:
        return KNOWN_DATA[bl_name]
    return None

fixed = 0
for ch in new_chars:
    name = ch['name']
    old = get_old_data(name)
    
    for field in ['manufacturer', 'weapon', 'code', 'burst']:
        if not ch.get(field) and old and old.get(field):
            ch[field] = old[field]
            fixed += 1
    
    # Class: special handling (old data uses 辅助, we use 支援)
    if not ch.get('class') and old and old.get('class'):
        val = old['class']
        if val == '辅助':
            val = '支援'
        ch['class'] = val
        fixed += 1
    
    # Convert any remaining 辅助 to 支援
    if ch.get('class') == '辅助':
        ch['class'] = '支援'
        fixed += 1

# Write
with open('data/characters.json', 'w', encoding='utf-8') as f:
    json.dump(new_chars, f, ensure_ascii=False, indent=2)

# Verify
classes = set()
empty_class = 0
empty_weapon = 0
for ch in new_chars:
    classes.add(ch.get('class', ''))
    if not ch.get('class', ''):
        empty_class += 1
    if not ch.get('weapon', ''):
        empty_weapon += 1

print(f'Fixed {fixed} fields')
print(f'Classes: {sorted(classes)}')
print(f'Empty class: {empty_class}')
print(f'Empty weapon: {empty_weapon}')
print(f'Total: {len(new_chars)}')

# List any remaining issues
if empty_class > 0:
    print('\nCharacters still missing class:')
    for c in new_chars:
        if not c.get('class', ''):
            print(f'  {c["name"]}')
