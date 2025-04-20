import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

# 默认文件路径
HEXAGRAM_FILE = Path("assets/64_Gua_Data.json")
YILIN_FILE    = Path("assets/64_Gua_Data_4096.json")

# 加载 JSON 数据
def load_json(path: Path) -> List[Dict]:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"错误：无法加载文件 {path}: {e}", file=sys.stderr)
        sys.exit(1)

def lookup_by_name(name: str, data: List[Dict], key: str = "六十四卦名") -> Optional[Dict]:
    return next((g for g in data if g.get(key) == name.strip()), None)

def _bits_to_binstr(bits: int) -> str:
    return format(bits, '06b')

def _compute_mutual_bits(bits: int) -> int:
    s = _bits_to_binstr(bits)
    return int(s[1:4] + s[2:5], 2)

def _compute_error_bits(bits: int) -> int:
    return bits ^ 0b111111

def _compute_zong_bits(bits: int) -> int:
    return int(_bits_to_binstr(bits)[::-1], 2)

def _determine_shiyao(orig_bits: int) -> int:
    lower = lambda b: b & 0b000111
    upper = lambda b: (b >> 3) & 0b000111
    is_pure = lambda b: lower(b) == upper(b)
    if is_pure(orig_bits):
        return 6
    work = orig_bits
    steps = [[1], [2], [3], [4], [5], [4], [1, 2, 3]]
    for group in steps:
        for pos in group:
            work ^= 1 << (pos - 1)
        if is_pure(work):
            return max(group)
    raise RuntimeError("世爻计算失败：七步内未得纯卦")

def other_hexagrams(bits_str: str) -> Dict[str, str]:
    try:
        bits_int = int(bits_str, 2)
    except ValueError:
        return {}
    return {
        "互卦": _bits_to_binstr(_compute_mutual_bits(bits_int)),
        "错卦": _bits_to_binstr(_compute_error_bits(bits_int)),
        "综卦": _bits_to_binstr(_compute_zong_bits(bits_int)),
    }

def _print_hexagram(g: Dict) -> None:
    print(f"卦名：{g.get('六十四卦名','未知')}（{g.get('六十四卦象','')}）")
    print(f"上卦：{g.get('上卦','-')}\n下卦：{g.get('下卦','-')}")
    bits = g.get('6_BIT','')
    if len(bits) == 6:
        try:
            shi = _determine_shiyao(int(bits,2))
            print(f"世爻：第 {shi} 爻")
        except RuntimeError as e:
            print(f"世爻计算错误：{e}", file=sys.stderr)
    print(f"杂卦：{g.get('杂卦','-')}")
    print(f"卦辞：{g.get('卦辞','-')}")
    print(f"大象：{g.get('大象','-')}")
    print(f"彖传：{g.get('彖传','-')}")

def print_single(g: Dict) -> None:
    print("\n===== 本卦查询 =====")
    _print_hexagram(g)
    bits = g.get('6_BIT','')
    if len(bits) == 6:
        for title, code in other_hexagrams(bits).items():
            hx = next((h for h in load_json(HEXAGRAM_FILE) if h.get('6_BIT') == code), None)
            if hx:
                print(f"\n===== {title} =====")
                _print_hexagram(hx)

def print_change(primary: Dict, line: int, changed: Dict, yilin: List[Dict]) -> None:
    print("\n===== 本卦（当前） =====")
    _print_hexagram(primary)

    print(f"\n===== 指定动爻：第 {line} 爻 =====")
    yarr = primary.get('爻辞', [])
    sx   = primary.get('小象', [])
    print(f"爻辞：{yarr[line-1] if 1<=line<=len(yarr) else '-'}")
    print(f"小象：{sx[line-1] if 1<=line<=len(sx) else '-'}")

    print("\n===== 变卦（结果） =====")
    _print_hexagram(changed)

    entry = next((e for e in yilin if e.get('本卦') == primary.get('六十四卦名') and e.get('变卦') == changed.get('六十四卦名')), None)
    print("\n===== 焦氏易林解 =====")
    print(entry.get('焦氏易林辞','无') if entry else "无对应记录。")

    bits = primary.get('6_BIT','')
    if len(bits) == 6:
        for title, code in other_hexagrams(bits).items():
            hx = next((h for h in load_json(HEXAGRAM_FILE) if h.get('6_BIT') == code), None)
            if hx:
                print(f"\n===== {title} =====")
                _print_hexagram(hx)

# ---------------------- 新增：封装交互流程 ----------------------

def interactive_query_single(hexagrams: List[Dict]) -> None:
    name = input("请输入卦名：").strip()
    g = lookup_by_name(name, hexagrams)
    if not g:
        print(f"错误：未找到卦 '{name}'。", file=sys.stderr)
    else:
        print_single(g)

def interactive_query_change(hexagrams: List[Dict], yilin: List[Dict]) -> None:
    p = input("本卦名称：").strip()
    ln = input("动爻 (1-6)：").strip()
    c = input("变卦名称：").strip()
    try:
        ln_i = int(ln)
    except ValueError:
        print("错误：动爻需为1-6的整数。", file=sys.stderr)
        return
    pri = lookup_by_name(p, hexagrams)
    chg = lookup_by_name(c, hexagrams)
    if not pri or not chg:
        print("错误：卦名未找到。", file=sys.stderr)
    elif not (1 <= ln_i <= 6):
        print("错误：动爻必须在1-6之间。", file=sys.stderr)
    else:
        print_change(pri, ln_i, chg, yilin)

def main_menu():
    hexagrams = load_json(HEXAGRAM_FILE)
    yilin = load_json(YILIN_FILE)

    print("请选择模式：")
    print("1: 本卦查询")
    print("2: 本卦-动爻-变卦-焦氏易林")
    mode = input("输入选项：").strip()

    if mode == '1':
        interactive_query_single(hexagrams)
    elif mode == '2':
        interactive_query_change(hexagrams, yilin)
    else:
        print("无效模式，程序退出。", file=sys.stderr)

# 保留脚本运行入口
if __name__ == '__main__':
    main_menu()
