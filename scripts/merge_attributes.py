#!/usr/bin/env python3
"""
用 BWIKI 已有属性数据补全角色信息
把 BWIKI 的简体名属性映射到正确的繁中名
"""

import json
import sys
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).parent.parent

# BWIKI 简体名 → 繁中名（slug） 映射
BWIKI_TO_SLUG = OrderedDict([
    ("艾德米", "admi"), ("诺薇儿", "novel"), ("米尔克", "milk"),
    ("波莉", "poli"), ("托比", "tove"), ("佩珀", "pepper"),
    ("爱丽丝", "alice"), ("安妮：奇迹仙女", "anne-miracle-fairy"),
    ("西格娜", "signal"), ("阿莉亚", "aria"), ("贝斯蒂", "vesti"),
    ("索林", "soline"), ("樱花", "sakura"), ("布丽德", "brid"),
    ("帕瓦", "power"), ("长发公主", "rapunzel"), ("吉萝婷", "guillotine"),
    ("鲁德米拉：冬日之主", "ludmilla-winter-owner"),
    ("桑迪", "centi"), ("艾菲涅尔", "epinel"), ("普琳玛", "primar"),
    ("神罚", "modernia"), ("梅登", "maiden"), ("白雪公主", "snow-white"),
    ("莱伊", "rei"), ("艾玛", "emma"), ("莱昂纳", "leona"),
    ("露菲", "rupee"), ("杨", "yan"), ("米卡：雪地伙伴", "mica-snow-buddy"),
    ("诺雅", "noah"), ("海伦", "helm"), ("舒格", "sugar"),
    ("桃乐丝", "dorothy"), ("麦斯威尔", "maxwell"), ("拉普拉斯", "laplace"),
    ("尤莉亚", "julia"), ("罗珊娜", "rosanna"), ("沃纶姆", "volume"),
    ("布兰儿", "blanc"), ("伊莎贝尔", "isabel"), ("鲁德米拉", "ludmilla"),
    ("豺狼", "jackal"), ("迪赛尔", "diesel"), ("毒蛇", "viper"),
    ("尤尔夏", "yulha"), ("德雷克", "drake"), ("红莲：暗影", "scarlet-black-shadow"),
    ("梅里：海湾女神", "bay-goddess-mary"), ("尤妮", "yuni"), 
    ("露菲：冬日购物狂", "rupee-winter-shopper"), ("米兰达", "miranda"),
    ("诺伊斯", "noise"), ("饼干", "biscuit"), ("红莲", "scarlet"),
    ("可可", "cocoa"), ("小红帽", "red-hood"), ("艾可希雅", "exia"),
    ("吉尔提", "guilty"), ("富克旺", "folkwang"), ("银华", "eunhwa"),
    ("克拉乌", "crow"), ("蒂亚", "tia"), ("丽塔", "liter"),
    ("普丽瓦蒂", "privaty"), ("索达", "soda"), ("哈兰", "harran"),
    ("诺亚尔", "noir"), ("朵拉", "dolla"),
])

# BWIKI 的字段
CLASS_MAP = {"辅助型": "辅助", "火力型": "火力", "防御型": "防御"}
BURST_MAP = {"1": "B1", "2": "B2", "3": "B3"}
CODE_MAP = {"风压": "风压", "水冷": "水冷", "铁甲": "铁甲", "燃烧": "燃烧", "电击": "电击", "风压": "风压"}
WEAPON_MAP = {"步枪": "AR", "狙击步枪": "SR", "霰弹枪": "SG", "发射器": "RL", "机枪": "MG", "冲锋枪": "SMG"}
MFG_MAP = {"极乐净土": "极乐净土", "泰特拉": "泰特拉", "米西利斯": "米西利斯", "朝圣者": "朝圣者", "反常": "反常"}

# 手动补充已知缺的（从 Prydwen 英文名推断）
# 格式: slug: {class, manufacturer, weapon, code, burst}
EXTRA_ATTRS = {
    # Recent 2025-2026
    "anis-star": {"class": "火力", "manufacturer": "泰特拉", "weapon": "RL", "code": "燃烧", "burst": "B2"},
    "neon-vision-eye": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SR", "code": "风压", "burst": "B3"},
    "white-crane": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SG", "code": "水冷", "burst": "B3"},
    "arcana-fortune-mate": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "RL", "code": "电击", "burst": "B2"},
    "eh": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SG", "code": "风压", "burst": "B3"},
    "chisato-nishikigi": {"class": "火力", "manufacturer": "反常", "weapon": "AR", "code": "电击", "burst": "B3"},
    "takina-inoue": {"class": "火力", "manufacturer": "反常", "weapon": "RL", "code": "铁甲", "burst": "B3"},
    "velvet": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "label": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SR", "code": "燃烧", "burst": "B3"},
    "snow-white-heavy-arms": {"class": "火力", "manufacturer": "朝圣者", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "diesel-winter-sweets": {"class": "防御", "manufacturer": "极乐净土", "weapon": "SMG", "code": "水冷", "burst": "B2"},
    "brid-silent-track": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "燃烧", "burst": "B3"},
    "maiden-ice-rose": {"class": "防御", "manufacturer": "极乐净土", "weapon": "RL", "code": "电击", "burst": "B3"},
    "guillotine-winter-slayer": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "soline-frost-ticket": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SMG", "code": "水冷", "burst": "B3"},
    "nayuta": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "SR", "code": "燃烧", "burst": "B2"},
    "liberalio": {"class": "火力", "manufacturer": "朝圣者", "weapon": "RL", "code": "风压", "burst": "B3"},
    "delta-ninja-thief": {"class": "防御", "manufacturer": "极乐净土", "weapon": "MG", "code": "水冷", "burst": "B2"},
    "ada-wong": {"class": "火力", "manufacturer": "反常", "weapon": "AR", "code": "燃烧", "burst": "B3"},
    "jill-valentine": {"class": "火力", "manufacturer": "反常", "weapon": "SMG", "code": "燃烧", "burst": "B3"},
    "ade-agent-bunny": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "milk-blooming-bunny": {"class": "火力", "manufacturer": "泰特拉", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "emma-tactical-upgrade": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "MG", "code": "燃烧", "burst": "B1"},
    "eunhwa-tactical-upgrade": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SR", "code": "燃烧", "burst": "B2"},
    "vesti-tactical-upgrade": {"class": "火力", "manufacturer": "极乐净土", "weapon": "RL", "code": "燃烧", "burst": "B3"},
    "dorothy-serendipity": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "elegg-boom-and-shock": {"class": "火力", "manufacturer": "米西利斯", "weapon": "MG", "code": "水冷", "burst": "B3"},
    "sakura-bloom-in-summer": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "燃烧", "burst": "B1"},
    "rosanna-chic-ocean": {"class": "火力", "manufacturer": "泰特拉", "weapon": "MG", "code": "电击", "burst": "B1"},
    "sora": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "RL", "code": "风压", "burst": "B1"},
    "eve": {"class": "火力", "manufacturer": "反常", "weapon": "SR", "code": "铁甲", "burst": "B3"},
    "raven": {"class": "火力", "manufacturer": "反常", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "k": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SMG", "code": "电击", "burst": "B3"},
    "arcana": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "RL", "code": "电击", "burst": "B2"},
    "mihara-bonding-chain": {"class": "火力", "manufacturer": "米西利斯", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "siren": {"class": "火力", "manufacturer": "朝圣者", "weapon": "RL", "code": "水冷", "burst": "B3"},
    "crust": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "RL", "code": "电击", "burst": "B2"},
    "bready": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SMG", "code": "风压", "burst": "B3"},
    "trina": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "RL", "code": "电击", "burst": "B2"},
    "asuka-shikinami-langley-wille": {"class": "火力", "manufacturer": "反常", "weapon": "SG", "code": "风压", "burst": "B3"},
    "anchor-innocent-maid": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "RL", "code": "水冷", "burst": "B2"},
    "mast-romantic-maid": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "MG", "code": "水冷", "burst": "B2"},
    "mana": {"class": "火力", "manufacturer": "米西利斯", "weapon": "AR", "code": "风压", "burst": "B3"},
    "quency-escape-queen": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SMG", "code": "水冷", "burst": "B3"},
    "alice-wonderland-bunny": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SR", "code": "水冷", "burst": "B3"},
    "soda-twinkling-bunny": {"class": "火力", "manufacturer": "泰特拉", "weapon": "RL", "code": "铁甲", "burst": "B3"},
    "aqua-marine-helm": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "铁甲", "burst": "B2"},
    "blue-ocean-neon": {"class": "火力", "manufacturer": "极乐净土", "weapon": "MG", "code": "水冷", "burst": "B3"},
    "bay-goddess-mary": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "水冷", "burst": "B1"},
    "rem": {"class": "火力", "manufacturer": "反常", "weapon": "MG", "code": "水冷", "burst": "B3"},
    "rapunzel-pure-grace": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "RL", "code": "铁甲", "burst": "B1"},
    "flora": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "MG", "code": "电击", "burst": "B2"},
    "privaty-unkind-maid": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SG", "code": "电击", "burst": "B3"},
    "d-killer-wife": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "SR", "code": "燃烧", "burst": "B1"},
    "2b": {"class": "火力", "manufacturer": "反常", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "a2": {"class": "火力", "manufacturer": "反常", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "makima": {"class": "防御", "manufacturer": "反常", "weapon": "MG", "code": "电击", "burst": "B2"},
    "sakura-suzuhara": {"class": "辅助", "manufacturer": "反常", "weapon": "SR", "code": "铁甲", "burst": "B1"},
    "sin": {"class": "防御", "manufacturer": "米西利斯", "weapon": "SMG", "code": "电击", "burst": "B2"},
    "nihilister": {"class": "火力", "manufacturer": "朝圣者", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "nero": {"class": "防御", "manufacturer": "泰特拉", "weapon": "SMG", "code": "铁甲", "burst": "B2"},
    "bay": {"class": "防御", "manufacturer": "泰特拉", "weapon": "MG", "code": "电击", "burst": "B2"},
    "ein": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SR", "code": "电击", "burst": "B2"},
    "trony": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SR", "code": "燃烧", "burst": "B3"},
    "kilo": {"class": "防御", "manufacturer": "米西利斯", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "elegg": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "MG", "code": "电击", "burst": "B2"},
    "asuka-shikinami-langley": {"class": "火力", "manufacturer": "反常", "weapon": "RL", "code": "水冷", "burst": "B3"},
    "rei-ayanami": {"class": "防御", "manufacturer": "反常", "weapon": "SMG", "code": "水冷", "burst": "B1"},
    "mari-makinami-illustrious": {"class": "火力", "manufacturer": "反常", "weapon": "SG", "code": "铁甲", "burst": "B3"},
    "rapi": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "燃烧", "burst": "B3"},
    "neon": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "SG", "code": "燃烧", "burst": "B1"},
    "anis": {"class": "防御", "manufacturer": "泰特拉", "weapon": "RL", "code": "铁甲", "burst": "B2"},
    "marciana": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "SG", "code": "铁甲", "burst": "B2"},
    "moran": {"class": "防御", "manufacturer": "泰特拉", "weapon": "SG", "code": "电击", "burst": "B1"},
    "naga": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "SG", "code": "电击", "burst": "B2"},
    "volume": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SMG", "code": "风压", "burst": "B1"},
    "mast": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "SMG", "code": "电击", "burst": "B2"},
    "crow": {"class": "防御", "manufacturer": "米西利斯", "weapon": "SMG", "code": "燃烧", "burst": "B3"},
    "shen": {"class": "防御", "manufacturer": "米西利斯", "weapon": "AR", "code": "电击", "burst": "B2"},
    "quency": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "SMG", "code": "电击", "burst": "B2"},
    "frima": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SG", "code": "铁甲", "burst": "B2"},
    "exia": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "电击", "burst": "B1"},
    "noir": {"class": "火力", "manufacturer": "泰特拉", "weapon": "AR", "code": "风压", "burst": "B3"},
    "yuni": {"class": "防御", "manufacturer": "米西利斯", "weapon": "RL", "code": "燃烧", "burst": "B2"},
    "julia": {"class": "火力", "manufacturer": "米西利斯", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "guilty": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SG", "code": "风压", "burst": "B2"},
    "sugar": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SG", "code": "铁甲", "burst": "B3"},
    # 额外补充
    "phantom": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "pleca": {"class": "火力", "manufacturer": "泰特拉", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "mary": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SG", "code": "水冷", "burst": "B1"},
    "d": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SMG", "code": "风压", "burst": "B3"},
    "clay": {"class": "火力", "manufacturer": "泰特拉", "weapon": "RL", "code": "水冷", "burst": "B3"},
    "rupee": {"class": "火力", "manufacturer": "泰特拉", "weapon": "AR", "code": "铁甲", "burst": "B2"},
    "mary-bay-goddess": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "水冷", "burst": "B1"},
    "snow-white-innocent-days": {"class": "火力", "manufacturer": "朝圣者", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "helm": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SR", "code": "水冷", "burst": "B3"},
    "maiden": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SG", "code": "电击", "burst": "B3"},
}


def main():
    # Load current data (193 characters from v4)
    input_path = BASE / "data" / "nikke_characters.json"
    with open(input_path, "r", encoding="utf-8") as f:
        chars = json.load(f)
    
    print(f"当前角色数: {len(chars)}", file=sys.stderr)
    
    # Apply BWIKI attributes
    bwiki_mapped = 0
    for c in chars:
        name_tw = c["name"]
        # Skip if already has attributes
        if c["class"]:
            continue
        
        # Try to find in BWIKI mapping
        slug = BWIKI_TO_SLUG.get(name_tw)
        if slug and slug in EXTRA_ATTRS:
            attrs = EXTRA_ATTRS[slug]
            c["class"] = attrs.get("class", "")
            c["manufacturer"] = attrs.get("manufacturer", "")
            c["weapon"] = attrs.get("weapon", "")
            c["code"] = attrs.get("code", "")
            c["burst"] = attrs.get("burst", "")
            bwiki_mapped += 1
    
    # Apply extra attributes for remaining
    extra_mapped = 0
    for c in chars:
        if c["class"]:
            continue
        # Find by slug in our Traditional_NAMES map
        from scrape_characters_v4 import TRADITIONAL_NAMES
        # Reverse lookup: find slug for this name
        slug = None
        for s, n in TRADITIONAL_NAMES.items():
            if n == c["name"]:
                slug = s
                break
        if slug and slug in EXTRA_ATTRS:
            attrs = EXTRA_ATTRS[slug]
            c["class"] = attrs.get("class", "")
            c["manufacturer"] = attrs.get("manufacturer", "")
            c["weapon"] = attrs.get("weapon", "")
            c["code"] = attrs.get("code", "")
            c["burst"] = attrs.get("burst", "")
            extra_mapped += 1
    
    with_attrs = sum(1 for c in chars if c["class"])
    missing = len(chars) - with_attrs
    
    print(f"BWIKI 映射: {bwiki_mapped}", file=sys.stderr)
    print(f"额外补充: {extra_mapped}", file=sys.stderr)
    print(f"有属性: {with_attrs}", file=sys.stderr)
    print(f"缺属性: {missing}", file=sys.stderr)
    
    # Save
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(chars, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {input_path}", file=sys.stderr)
    
    # Print stats
    from collections import Counter
    mfg_dist = Counter(c.get("manufacturer", "(未知)") for c in chars if c["manufacturer"])
    print(f"\n企业分布:", file=sys.stderr)
    for m, n in mfg_dist.most_common():
        print(f"  {m}: {n}", file=sys.stderr)
    
    # Show missing
    if missing:
        print(f"\n缺属性的角色 ({missing}):", file=sys.stderr)
        for c in chars:
            if not c["class"]:
                print(f"  {c['name']}", file=sys.stderr)


if __name__ == "__main__":
    main()
