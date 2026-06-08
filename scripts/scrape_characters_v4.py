#!/usr/bin/env python3
"""
NIKKE 角色数据采集 v4
合并三个数据源：
1. Prydwen slugs → 完整角色名单
2. 巴哈姆特 → 正確繁中名
3. BWIKI → 属性数据（已有的）
"""

import json
import re
import sys
from pathlib import Path
from collections import OrderedDict

import requests

PRYDWEN_URL = "https://www.prydwen.gg/nikke/tier-list"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ── 繁體中文名映射（slug → 繁中名，來自巴哈姆特）──
TRADITIONAL_NAMES = OrderedDict([
    # 2026
    ("pleca", "普莉卡"), ("mint", "敏特"), ("anis-star", "阿妮斯:超級巨星"),
    ("neon-vision-eye", "尼恩:透視之眼"), ("white-crane", "白鶴"),
    ("arcana-fortune-mate", "阿爾卡娜:命運伴侶"), ("eh", "E.H."),
    ("chisato-nishikigi", "錦木千束"), ("takina-inoue", "井之上瀧奈"),
    ("velvet", "薇爾維特"), ("label", "蕾貝兒"),
    ("snow-white-heavy-arms", "白雪公主:重型武裝"),
    # 2025
    ("diesel-winter-sweets", "迪塞爾:冬日甜心"), ("brid-silent-track", "布麗德:靜默軌道"),
    ("maiden-ice-rose", "梅登:冰玫瑰"), ("guillotine-winter-slayer", "梅吉蘿婷:寒冬殺手"),
    ("soline-frost-ticket", "索林:霜雪車票"), ("nayuta", "娜由塔"), ("liberalio", "莉貝雷利奧"),
    ("delta-ninja-thief", "德爾塔:怪盜忍者"), ("ada-wong", "艾達·王"),
    ("jill-valentine", "吉兒·華倫泰"), ("ade-agent-bunny", "愛德:特務兔女郎"),
    ("milk-blooming-bunny", "米爾克:花漾兔女郎"),
    ("emma-tactical-upgrade", "艾瑪:戰術升級"), ("eunhwa-tactical-upgrade", "銀華:戰術升級"),
    ("vesti-tactical-upgrade", "貝斯蒂:戰術升級"),
    ("dorothy-serendipity", "桃樂絲:機緣巧遇"), ("elegg-boom-and-shock", "伊萊格:BOOM與驚嚇"),
    ("sakura-bloom-in-summer", "櫻花:夏日綻放"), ("rosanna-chic-ocean", "羅珊娜:高雅海洋"),
    ("sora", "索拉"), ("eve", "伊芙"), ("raven", "雷雯"),
    ("k", "K"), ("arcana", "阿爾卡娜"),
    ("mihara-bonding-chain", "米哈拉:羈絆鎖鏈"), ("siren", "小美人魚"),
    ("crust", "克勞斯特"), ("bready", "布蕾德"), ("trina", "特蕾娜"),
    ("asuka-shikinami-langley-wille", "式波·明日香·蘭格雷：WILLE"),
    ("anchor-innocent-maid", "安克:天真的女僕"),
    ("mast-romantic-maid", "馬斯特:浪漫的女僕"),
    ("mana", "瑪娜"), ("rapi-red-hood", "拉毗:小紅帽"),
    ("scarlet-black-shadow", "紅蓮:暗影"),
    # 2024
    ("cinderella", "灰姑娘"), ("grave", "格拉維"), ("flora", "芙蘿拉"),
    ("crown", "皇冠"), ("quency-escape-queen", "坎西:逃生女王"),
    ("mica-snow-buddy", "米卡:雪地夥伴"), ("ludmilla-winter-owner", "魯德米拉:冬日之主"),
    ("soda-twinkling-bunny", "索達:閃亮兔女郎"), ("alice-wonderland-bunny", "愛麗絲:仙境兔女郎"),
    ("aqua-marine-helm", "海倫:海藍寶石"), ("anis-sparkling-summer", "阿妮斯:閃耀夏日"),
    ("blue-ocean-neon", "尼恩:藍色海洋"), ("bay-goddess-mary", "梅里:海灣女神"),
    ("rem", "雷姆"), ("emilia", "愛蜜莉雅"),
    ("rapunzel-pure-grace", "長髮公主:純白承諾"),
    ("rupee-winter-shopper", "露菲:冬日購物狂"),
    ("anne-miracle-fairy", "安妮:奇蹟仙女"),
    # 2023
    ("red-hood", "小紅帽"), ("dorothy", "桃樂絲"), ("modernia", "神罰"),
    ("2b", "2B"), ("a2", "A2"), ("makima", "真紀真"), ("power", "帕瓦"),
    ("privaty-unkind-maid", "普麗瓦蒂:不友善的女僕"),
    ("d-killer-wife", "D:殺手妻子"),
    ("asuka-shikinami-langley", "式波·明日香·蘭格雷"),
    ("rei-ayanami", "綾波零"), ("mari-makinami-illustrious", "真希波·真理·伊拉絲多莉雅斯"),
    # 開服常駐
    ("scarlet", "紅蓮"), ("harran", "哈蘭"), ("snow-white", "白雪公主"),
    ("isabel", "伊莎貝爾"), ("rapunzel", "長髮公主"), ("noah", "諾雅"),
    ("noise", "諾伊斯"), ("biscuit", "餅乾"), ("jackal", "豺狼"),
    ("centi", "森提"), ("dolla", "朵拉"), ("liter", "麗塔"),
    ("pepper", "佩珀"), ("admi", "艾德米"), ("privaty", "普麗瓦蒂"),
    ("helm", "海倫"), ("brid", "布麗德"), ("maiden", "梅登"),
    ("guillotine", "吉蘿婷"), ("laplace", "拉普拉斯"), ("maxwell", "麥斯威爾"),
    ("drake", "德雷克"), ("alice", "愛麗絲"), ("sugar", "舒格"),
    ("rapi", "拉毗"), ("neon", "尼恩"), ("anis", "阿妮斯"),
    ("rupee", "露菲"), ("soda", "索達"), ("yan", "楊"),
    ("milk", "米爾克"), ("yulha", "尤爾夏"), ("vesti", "貝斯蒂"),
    ("epinel", "艾菲涅爾"), ("diesel", "迪塞爾"), ("cocoa", "可可"),
    ("soline", "索林"), ("sakura", "櫻花"), ("novel", "諾薇兒"),
    ("mihara", "米哈拉"), ("frima", "芙里瑪"), ("exia", "艾可希雅"),
    ("julia", "尤莉亞"), ("yuni", "尤妮"), ("rosanna", "羅珊娜"),
    ("mast", "馬斯特"), ("marciana", "瑪律恰那"), ("ludmilla", "魯德米拉"),
    ("moran", "莫蘭"), ("naga", "娜嘉"), ("tia", "蒂亞"),
    ("tove", "托比"), ("folkwang", "富克旺"), ("volume", "沃綸姆"),
    ("eunhwa", "銀華"), ("miranda", "米蘭達"), ("poli", "波莉"),
    ("signal", "西格娜"), ("blanc", "布蘭兒"), ("noir", "諾瓦"),
    ("aria", "阿莉亞"), ("leona", "萊昂納"), ("viper", "毒蛇"),
    ("crow", "克拉烏"), ("quency", "坎西"), ("shen", "森"),
    ("guilty", "吉爾提"), ("sin", "辛"), ("nihilister", "尼希利斯塔"),
    ("nero", "尼羅"), ("bay", "蓓"), ("ein", "愛因"),
    ("trony", "特羅尼"), ("kilo", "吉洛"), ("elegg", "伊萊格"),
    ("mica", "米卡"), ("belorta", "貝洛塔"), ("neve", "尼夫"),
    ("anchor", "安克"), ("pascal", "帕斯卡"), ("ether", "伊賽爾"),
    # R/SR
    ("product-08", "產品08"), ("product-12", "產品12"), ("product-23", "產品23"),
    ("soldier-eg", "士兵E.G."), ("soldier-fa", "士兵F.A."), ("soldier-ow", "士兵O.W."),
    ("idoll-flower", "iDoll花"), ("idoll-ocean", "iDoll海"), ("idoll-sun", "iDoll太陽"),
    ("n102", "N102"),
    # 其他
    ("chime", "查咪"), ("quiry", "奎里"), ("mori", "莫里"),
    ("lily", "莉莉"), ("snow-crane", "雪鶴"), ("avistar", "阿維斯塔"),
    ("rouge", "魯吉"), ("himeno", "姬野"),
    ("claire-redfield", "克蕾兒·雷德費爾德"),
    ("misato-katsuragi", "葛城美里"),
    ("sakura-suzuhara", "鈴原櫻"), ("kurumi", "紅胡桃"),
    ("ram", "拉姆"), ("rei", "蕾伊"),
    # 特殊
    ("bay-treasure", "蓓（收藏品）"),
    ("centi-treasure", "森提（收藏品）"),
    ("diesel-treasure", "迪塞爾（收藏品）"),
    ("drake-treasure", "德雷克（收藏品）"),
    ("exia-treasure", "艾可希雅（收藏品）"),
    ("frima-treasure", "芙里瑪（收藏品）"),
    ("helm-treasure", "海倫（收藏品）"),
    ("julia-treasure", "尤莉亞（收藏品）"),
    ("laplace-treasure", "拉普拉斯（收藏品）"),
    ("milk-treasure", "米爾克（收藏品）"),
    ("miranda-treasure", "米蘭達（收藏品）"),
    ("poli-treasure", "波莉（收藏品）"),
    ("privaty-treasure", "普麗瓦蒂（收藏品）"),
    ("tove-treasure", "托比（收藏品）"),
    ("viper-treasure", "毒蛇（收藏品）"),
    ("zwei-treasure", "茨瓦伊（收藏品）"),
    ("moran-treasure", "莫蘭（收藏品）"),
    ("zwei", "茨瓦伊"),
])

# 已知属性数据（手动维护的 PVP 关键角色 + BWIKI 已有数据）
# 格式: {slug: {class, manufacturer, weapon, code, burst}}
KNOWN_ATTRIBUTES = {
    # 朝圣者
    "scarlet": {"class": "火力", "manufacturer": "朝圣者", "weapon": "AR", "code": "电击", "burst": "B3"},
    "scarlet-black-shadow": {"class": "火力", "manufacturer": "朝圣者", "weapon": "RL", "code": "风压", "burst": "B3"},
    "modernia": {"class": "火力", "manufacturer": "朝圣者", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "snow-white": {"class": "火力", "manufacturer": "朝圣者", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "snow-white-heavy-arms": {"class": "火力", "manufacturer": "朝圣者", "weapon": "AR", "code": "铁甲", "burst": "B3"},
    "harran": {"class": "火力", "manufacturer": "朝圣者", "weapon": "SR", "code": "电击", "burst": "B3"},
    "isabel": {"class": "火力", "manufacturer": "朝圣者", "weapon": "SG", "code": "电击", "burst": "B3"},
    "rapunzel": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "RL", "code": "铁甲", "burst": "B1"},
    "rapunzel-pure-grace": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "RL", "code": "铁甲", "burst": "B1"},
    "noah": {"class": "防御", "manufacturer": "朝圣者", "weapon": "RL", "code": "风压", "burst": "B2"},
    "noise": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "RL", "code": "电击", "burst": "B1"},
    "dorothy": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "dorothy-serendipity": {"class": "辅助", "manufacturer": "朝圣者", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "cinderella": {"class": "火力", "manufacturer": "朝圣者", "weapon": "RL", "code": "风压", "burst": "B3"},
    "crown": {"class": "防御", "manufacturer": "朝圣者", "weapon": "RL", "code": "燃烧", "burst": "B2"},
    "grave": {"class": "防御", "manufacturer": "朝圣者", "weapon": "RL", "code": "铁甲", "burst": "B2"},
    "red-hood": {"class": "火力", "manufacturer": "朝圣者", "weapon": "SR", "code": "铁甲", "burst": "全"},
    "siren": {"class": "火力", "manufacturer": "朝圣者", "weapon": "RL", "code": "水冷", "burst": "B3"},
    "nihilister": {"class": "火力", "manufacturer": "朝圣者", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    "rapi-red-hood": {"class": "火力", "manufacturer": "朝圣者", "weapon": "MG", "code": "燃烧", "burst": "B3"},
    # PVP 热门
    "jackal": {"class": "防御", "manufacturer": "米西利斯", "weapon": "RL", "code": "铁甲", "burst": "B1"},
    "biscuit": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "RL", "code": "铁甲", "burst": "B2"},
    "centi": {"class": "防御", "manufacturer": "泰特拉", "weapon": "RL", "code": "水冷", "burst": "B2"},
    "blanc": {"class": "防御", "manufacturer": "泰特拉", "weapon": "AR", "code": "风压", "burst": "B2"},
    "noir": {"class": "火力", "manufacturer": "泰特拉", "weapon": "AR", "code": "风压", "burst": "B2"},
    "anis-sparkling-summer": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SG", "code": "水冷", "burst": "B3"},
    "she": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SG", "code": "水冷", "burst": "B3"},
    "alice": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SR", "code": "燃烧", "burst": "B3"},
    "maxwell": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SR", "code": "铁甲", "burst": "B3"},
    "emilia": {"class": "辅助", "manufacturer": "反常", "weapon": "AR", "code": "燃烧", "burst": "B3"},
    "anis-star": {"class": "火力", "manufacturer": "泰特拉", "weapon": "RL", "code": "燃烧", "burst": "B2"},
    # 充能辅助
    "dolla": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "风压", "burst": "B2"},
    "liter": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "SMG", "code": "铁甲", "burst": "B1"},
    "sakura": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "燃烧", "burst": "B1"},
    "pepper": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "SG", "code": "风压", "burst": "B1"},
    "tove": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "AR", "code": "水冷", "burst": "B1"},
    "privacy": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "novel": {"class": "防御", "manufacturer": "泰特拉", "weapon": "SMG", "code": "铁甲", "burst": "B2"},
    # 增加 BWIKI 已有的
    "vesti": {"class": "火力", "manufacturer": "极乐净土", "weapon": "RL", "code": "水冷", "burst": "B3"},
    "yulha": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SR", "code": "燃烧", "burst": "B3"},
    "epinel": {"class": "火力", "manufacturer": "米西利斯", "weapon": "SMG", "code": "风压", "burst": "B3"},
    "signal": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SMG", "code": "燃烧", "burst": "B2"},
    "soline": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SMG", "code": "铁甲", "burst": "B3"},
    "brid": {"class": "火力", "manufacturer": "极乐净土", "weapon": "AR", "code": "水冷", "burst": "B3"},
    "diesel": {"class": "防御", "manufacturer": "极乐净土", "weapon": "MG", "code": "风压", "burst": "B2"},
    "cocoa": {"class": "辅助", "manufacturer": "泰特拉", "weapon": "SR", "code": "燃烧", "burst": "B1"},
    "milk": {"class": "火力", "manufacturer": "泰特拉", "weapon": "SR", "code": "水冷", "burst": "B1"},
    "eunhwa": {"class": "火力", "manufacturer": "极乐净土", "weapon": "SR", "code": "燃烧", "burst": "B2"},
    "miranda": {"class": "辅助", "manufacturer": "极乐净土", "weapon": "SMG", "code": "燃烧", "burst": "B1"},
    "poli": {"class": "防御", "manufacturer": "极乐净土", "weapon": "SG", "code": "水冷", "burst": "B2"},
    "admi": {"class": "辅助", "manufacturer": "米西利斯", "weapon": "SR", "code": "风压", "burst": "B2"},
}


def main():
    print("获取 Prydwen 角色列表...", file=sys.stderr)
    resp = requests.get(PRYDWEN_URL, headers=HEADERS, timeout=15)
    slugs = sorted(set(re.findall(r'/nikke/characters/([a-z0-9-]+)', resp.text)))
    print(f"  共 {len(slugs)} 个", file=sys.stderr)

    characters = []
    seen = set()

    for slug in slugs:
        if slug in ("tier-list", ""):
            continue

        # 繁中名
        name_tw = TRADITIONAL_NAMES.get(slug, slug.replace("-", " ").title())
        name_en = " ".join(w.capitalize() for w in slug.replace("-", " ").split())

        # 属性
        attrs = KNOWN_ATTRIBUTES.get(slug, {})

        char = {
            "name": name_tw,
            "name_slug": slug,
            "class": attrs.get("class", ""),
            "manufacturer": attrs.get("manufacturer", ""),
            "weapon": attrs.get("weapon", ""),
            "code": attrs.get("code", ""),
            "burst": attrs.get("burst", ""),
        }

        if name_tw not in seen:
            seen.add(name_tw)
            characters.append(char)

    # 只保留 SSR（通过已知名单判断，移除非SSR）
    non_ssr_slugs = {
        "product-08", "product-12", "product-23",
        "soldier-eg", "soldier-fa", "soldier-ow",
        "idoll-flower", "idoll-ocean", "idoll-sun",
        "n102", "mica", "belorta", "neve", "anchor",
        "soldier-eg", "neve", "ether",
        "mica", "belorta", "anchor",
    }
    ssr = [c for c in characters if c["name_slug"] not in non_ssr_slugs]

    # 去重（有些同角色不同版本）
    seen_names = set()
    ssr_deduped = []
    for c in ssr:
        if c["name"] not in seen_names:
            seen_names.add(c["name"])
            ssr_deduped.append(c)

    # 输出
    output = Path(__file__).parent.parent / "data" / "nikke_characters.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(ssr_deduped, f, ensure_ascii=False, indent=2)

    with_attrs = sum(1 for c in ssr_deduped if c["class"])
    print(f"\n✅ 完成!", file=sys.stderr)
    print(f"  SSR 角色: {len(ssr_deduped)}", file=sys.stderr)
    print(f"  有属性: {with_attrs}", file=sys.stderr)
    print(f"  缺属性: {len(ssr_deduped) - with_attrs}", file=sys.stderr)
    print(f"  文件: {output}", file=sys.stderr)

    # 打印有属性的
    print(f"\n{'繁中名':25s} | {'职业':4s} | {'企业':5s} | {'武器':3s} | {'代码':4s} | {'爆裂':2s}")
    print("-" * 55)
    for c in ssr_deduped:
        if c["class"]:
            print(f"{c['name']:25s} | {c['class']:4s} | {c['manufacturer']:5s} | {c['weapon']:3s} | {c['code']:4s} | {c['burst']:2s}")
    print(f"\n（缺属性的未显示，共 {len(ssr_deduped) - with_attrs} 个）")


if __name__ == "__main__":
    main()
