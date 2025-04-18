"""
gua_lookup.py
-------------------------------------------------------------------------
提供 query_hexagram() — 外部唯一接口
"""

from typing import List, Optional
import json
import sys

# 默认常量（可被主脚本覆盖）
HEXAGRAM_DATA_FILE = "assets/64_Gua_Data.json"
JIAO_SHI_DATA_FILE = "assets/64_Gua_Data_4096.json"


# ---------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------
def _load_json(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {path} 失败：{e}", file=sys.stderr)
        return []


def _lookup_hexagram_by_name(name: str, data: list) -> Optional[dict]:
    return next((g for g in data if g.get("六十四卦名") == name.strip()), None)


def _normalize_bits(bits: str) -> str:
    """参照原规则：首位为 1 时全反转"""
    return bits if bits[0] == "0" else "".join("1" if b == "0" else "0" for b in bits)


def _other_hexagrams(primary_bits: str) -> dict:
    """返回互卦、错卦、综卦的 7 位码"""
    mutual = _normalize_bits("0" + primary_bits[2:5] + primary_bits[3:6])
    error  = _normalize_bits("0" + "".join("1" if b == "0" else "0" for b in primary_bits[1:]))
    zong   = _normalize_bits("0" + primary_bits[1:][::-1])
    return {"互卦": mutual, "错卦": error, "综卦": zong}


def _print_hexagram(title: str, hexagram: dict, *,
                    moving_line: int | None = None, simplified: bool = True) -> None:
    print(f"\n===== {title} =====")
    print(f"卦名：{hexagram.get('六十四卦名','未知')}（{hexagram.get('六十四卦象','无')}）")
    print(f"上卦：{hexagram.get('上卦','无')}")
    print(f"下卦：{hexagram.get('下卦','无')}")
    print(f"杂卦：{hexagram.get('杂卦','无')}")
    if not simplified:
        print(f"7_BIT：{hexagram.get('7_BIT','未知')}")
    print(f"卦辞：{hexagram.get('卦辞','无')}")
    print(f"大象：{hexagram.get('大象','无')}")

    if moving_line:
        yarrow = hexagram.get("爻辞", [])
        small  = hexagram.get("小象", [])
        if 1 <= moving_line <= len(yarrow):
            print(f"\n-- 指定动爻：第 {moving_line} 爻 --")
            print(f"爻辞：{yarrow[moving_line-1]}")
            print(f"小象：{small[moving_line-1] if 0 <= moving_line-1 < len(small) else '无'}")
        else:
            print(f"未找到第 {moving_line} 爻的爻辞")


# ---------------------------------------------------------------------
# 对外 API
# ---------------------------------------------------------------------
def query_hexagram(
    *,
    primary_name: str,
    moving_line: int,
    changed_name: str,
    simplified: bool = True,
    hex_file: str = HEXAGRAM_DATA_FILE,
    jiao_file: str = JIAO_SHI_DATA_FILE,
) -> None:
    """
    输入固定，按指定动爻输出所有相关卦象信息
    """
    hexagrams = _load_json(hex_file)
    jiao_data = _load_json(jiao_file)

    primary_hex = _lookup_hexagram_by_name(primary_name, hexagrams)
    changed_hex = _lookup_hexagram_by_name(changed_name, hexagrams)

    if not primary_hex:
        print(f"错误：未找到本卦“{primary_name}”", file=sys.stderr)
        return
    if not changed_hex:
        print(f"错误：未找到变卦“{changed_name}”", file=sys.stderr)
        return
    if not (1 <= moving_line <= 6):
        print("错误：动爻必须在 1‑6 之间", file=sys.stderr)
        return

    # ---- 本卦 & 变卦 ----
    _print_hexagram("本卦（当前状态）", primary_hex,
                    moving_line=moving_line, simplified=simplified)
    _print_hexagram("变卦（预测结果）", changed_hex,
                    moving_line=None, simplified=simplified)

    # ---- 焦氏易林 ----
    entry = next((e for e in jiao_data
                  if e.get("本卦") == primary_name and e.get("变卦") == changed_name), None)
    print("\n===== 焦氏易林解 =====")
    if entry:
        print(f"本卦：{entry.get('本卦')}")
        print(f"变卦：{entry.get('变卦')}")
        print(f"焦氏易林辞：{entry.get('焦氏易林辞','无')}")
    else:
        print("未找到对应焦氏易林记录。")

    # ---- 互 / 错 / 综 卦 ----
    bits = primary_hex.get("7_BIT")
    if bits and len(bits) == 7:
        for title, b in _other_hexagrams(bits).items():
            hx = next((g for g in hexagrams if g.get("7_BIT") == b), None)
            if hx:
                _print_hexagram(f"{title}", hx, simplified=simplified)
