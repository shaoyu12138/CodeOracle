import json
import random
from datetime import datetime

# --- 文件路径常量 ---
HEXAGRAM_DATA_FILE = "assets/64_Gua_Data.json" # 六十四卦基础数据文件
JIAO_SHI_DATA_FILE = "assets/64_Gua_Data_4096.json" # 焦氏易林数据文件 (本卦->变卦)


def prompt_user_input(output):
    """
    获取用户输入（性别、背景、问题），并添加到输出列表。

    :param output: 存储占卜过程记录的列表
    :return: 用户性别（"0"或"1"）和用户问题（字符串）
    """
    while True:
        gender_input = input("请输入性别（0为男，1为女）：").strip()
        if gender_input in ["0", "1"]:
            break
        print("输入错误，请输入0或1。")

    background = input("请输入您的问题背景：").strip()
    question = input("请输入您的问题：").strip()

    output.append(f"\n## 占卜\n- 您的问题背景：{background}")
    output.append(f"\n- 您的问题：{question}")
    output.append("\n- 你的解卦：")
    return gender_input, question

def generate_primary_hexagram_binary(gender):
    """
    生成本卦的初始7位二进制表示（性别位+6位随机数）。

    :param gender: 用户性别（"0"或"1"）
    :return: 7位二进制字符串
    """
    random_number = random.getrandbits(6)
    six_bit = format(random_number, '06b')
    return str(gender) + six_bit

def normalize_hexagram_binary(binary_str):
    """
    规范化7位二进制字符串：首位为'1'时，各位取反；否则不变。

    :param binary_str: 7位二进制字符串
    :return: 规范化后的7位二进制字符串，若输入无效则返回"0000000"
    """
    if not binary_str or len(binary_str) != 7:
        return "0000000"
    return binary_str if binary_str[0] == '0' else ''.join('1' if bit == '0' else '0' for bit in binary_str)

def load_hexagram_data(file_path):
    """
    从指定的JSON文件加载卦数据列表。

    :param file_path: JSON文件路径
    :return: 卦数据（列表），若失败则返回空列表
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 格式错误，无法解析JSON。")
        return []
    except Exception as e:
        print(f"加载 {file_path} 时发生未知错误: {e}")
        return []

def load_jiao_shi_yi_lin_data(file_path):
    """
    从指定的JSON文件中加载焦氏易林数据列表。

    :param file_path: JSON文件路径
    :return: 焦氏易林数据（列表），若失败则返回空列表
    """
    return load_hexagram_data(file_path)

def lookup_hexagram(binary_str, hexagrams):
    """
    根据7位二进制字符串在卦数据列表中查找对应卦象。

    :param binary_str: 7位二进制字符串
    :param hexagrams: 卦数据（列表）
    :return: 匹配的卦象字典，未找到则返回None
    """
    return next((hexagram for hexagram in hexagrams if hexagram.get("7_BIT") == binary_str), None)

def lookup_jiao_shi_yi_lin(primary_name, changed_name, jiao_shi_data):
    """
    根据本卦和变卦名称查找焦氏易林条目。

    :param primary_name: 本卦名称
    :param changed_name: 变卦名称
    :param jiao_shi_data: 焦氏易林数据（列表）
    :return: 匹配的焦氏易林字典，未找到则返回None
    """
    return next((entry for entry in jiao_shi_data
                 if entry.get("本卦") == primary_name and entry.get("变卦") == changed_name), None)


def fetch_yarrow_line(binary_str, hexagrams):
    """
    获取指定卦象的爻辞列表，并随机选择一个动爻（爻数和爻辞）。

    :param binary_str: 7位二进制字符串
    :param hexagrams: 卦数据（列表）
    :return: (动爻数, 对应爻辞) 或 (None, 错误提示)
    """
    hexagram = lookup_hexagram(binary_str, hexagrams)
    if not hexagram:
        return None, "未找到对应的卦象"

    yarrow_texts = hexagram.get("爻辞", [])
    if not yarrow_texts:
        return None, "该卦没有爻辞"

    moving_line_count = random.randint(1, len(yarrow_texts))
    if 1 <= moving_line_count <= len(yarrow_texts):
         return moving_line_count, yarrow_texts[moving_line_count - 1]
    else:
        return None, "无法确定有效的动爻"


def create_moving_line_mask(moving_line_count):
    """
    根据动爻数生成7位二进制掩码（右侧填充1）。

    :param moving_line_count: 动爻数 (1-6)
    :return: 7位二进制掩码字符串 (如 动爻数3 -> "0000111")
    """
    return ('1' * moving_line_count).rjust(7, '0') if moving_line_count and moving_line_count > 0 else "0000000"

def display_hexagram(title, binary_str, hexagrams, output, simplified, show_moving_info=True):
    """
    查找、格式化并记录卦象信息到输出列表，返回动爻数和卦名。

    :param title: 卦的类型标题 (e.g., "本卦")
    :param binary_str: 7位二进制字符串
    :param hexagrams: 卦数据（列表）
    :param output: 存储占卜过程记录的列表
    :param simplified: 是否简化输出（隐藏二进制和掩码）
    :param show_moving_info: 是否查找并显示动爻信息
    :return: 元组 (动爻数或None, 卦名或None)
    """
    hexagram = lookup_hexagram(binary_str, hexagrams)
    if not hexagram:
        output.append(f"未找到二进制 {binary_str} 对应的{title}。")
        return None, None # 返回 None 表示未找到

    hexagram_name = hexagram.get('六十四卦名', '未知卦名')
    moving_line_count = None
    yarrow_line = None
    mask = "0000000"

    if show_moving_info:
        moving_line_count, yarrow_line_or_error = fetch_yarrow_line(binary_str, hexagrams)
        if moving_line_count is not None:
            yarrow_line = yarrow_line_or_error
            mask = create_moving_line_mask(moving_line_count)
        else:
            output.append(f"{title} 获取动爻信息失败: {yarrow_line_or_error}")

    output.append(f"\n===== {title} 相关信息 =====")
    output.append(f"卦名：{hexagram_name} ({hexagram.get('六十四卦象', '无')})")
    output.append(f"上卦：{hexagram.get('上卦', '无')}")
    output.append(f"下卦：{hexagram.get('下卦', '无')}")
    output.append(f"杂卦：{hexagram.get('杂卦', '无')}")
    output.append(f"彖传：{hexagram.get('彖传', '无')}")

    if not simplified:
        output.append(f"{title} 二进制：{binary_str}")

    output.append(f"卦辞：{hexagram.get('卦辞', '无')}")
    output.append(f"大象：{hexagram.get('大象', '无')}")

    if show_moving_info and moving_line_count is not None and yarrow_line is not None:
        output.append(f"动爻：第 {moving_line_count} 爻")
        if not simplified:
            output.append(f"{title} 动爻掩码：{mask}")
        output.append(f"爻辞：{yarrow_line}")

        small_xiang_list = hexagram.get("小象", [])
        if isinstance(small_xiang_list, list) and 0 <= moving_line_count - 1 < len(small_xiang_list):
             output.append(f"小象：{small_xiang_list[moving_line_count - 1]}")
        else:
            output.append("小象：无对应的小象信息")

    # 返回动爻数（如果是本卦且找到动爻）和卦名
    moving_line_to_return = moving_line_count if show_moving_info and moving_line_count is not None else None
    return moving_line_to_return, hexagram_name


def compute_changed_hexagram(primary_binary, moving_line_count, simplified, output):
    """
    根据本卦二进制和动爻数计算变卦的7位二进制表示。
    计算逻辑：生成动爻掩码，与7位随机数AND，结果再与本卦OR，最后规范化。

    :param primary_binary: 本卦的规范化7位二进制字符串
    :param moving_line_count: 本卦的动爻数
    :param simplified: 是否简化输出（隐藏计算过程）
    :param output: 存储占卜过程记录的列表
    :return: 规范化后的变卦7位二进制字符串, 或在无效输入时返回 None
    """
    if not primary_binary or len(primary_binary) != 7 or moving_line_count is None or moving_line_count <= 0:
         output.append("\n错误：计算变卦所需参数无效。")
         return None # 返回 None 表示计算失败

    moving_mask = create_moving_line_mask(moving_line_count)
    random_bits = format(random.getrandbits(7), '07b')

    # 实际影响变爻的掩码：随机位和动爻掩码位都为1的部分
    actual_mask = ''.join('1' if rb == '1' and mb == '1' else '0'
                          for rb, mb in zip(random_bits, moving_mask))

    # 将实际变爻掩码应用到本卦上（按位或）
    or_result = ''.join('1' if pb == '1' or am == '1' else '0'
                        for pb, am in zip(primary_binary, actual_mask))

    # 规范化得到最终的变卦二进制
    changed_binary = normalize_hexagram_binary(or_result)

    if not simplified:
        output.append("\n----- 变卦计算过程 -----")
        output.append(f"本卦二进制数           : {primary_binary}")
        output.append(f"动爻数                 : {moving_line_count}")
        output.append(f"本卦动爻掩码           : {moving_mask}")
        output.append(f"生成的随机二进制数       : {random_bits}")
        output.append(f"随机数与动爻掩码按位与结果 : {actual_mask}")
        output.append(f"与本卦二进制数按位或结果 : {or_result}")
        output.append(f"规范化后的变卦二进制数     : {changed_binary}")

    return changed_binary

def perform_divination(hex_json_file_path, jiao_shi_json_file_path, simplified=True, print_extra=False):
    """
    执行完整的占卜流程：获取输入、生成各卦、查找信息、输出结果到文件。

    :param hex_json_file_path: 六十四卦基础数据的JSON文件路径
    :param jiao_shi_json_file_path: 焦氏易林数据的JSON文件路径
    :param simplified: 是否简化输出（默认True）
    :param print_extra: 是否显示互、错、综卦的动爻信息（默认False）
    """
    output = [
        "- 你是一个喜欢明确解卦并带有倾向性的解卦师，擅长提供具有明确观点的卦象分析与给予指导意见。\n"
        "- 解卦须知：本卦代表当前状态，变卦表示预测，互卦反映内在原因、错卦反映不足和应对策略，综卦反映潜在困难。变卦是多爻变的特殊占法，契合《焦氏易林》的64*64 =4096种可能。本质是从初爻到动爻之间，所有的爻都可能变动。\n"
        "> 特别提示：请重点关注本卦和动爻还有焦氏易林解的信息。所有的卦都是以本卦为出发点构建的。\n"
        "> 解卦流程：结合占卜背景和问题，逐步解读每个卦象。你的回答分为三个部分：一，首先复述卦象所有内容（卦名，彖传，卦辞，大象，爻辞，小象），并提供文言文翻译。二，其次进行详细分析和解读和指导建议。三，最后一段，根据输入信息及卦象所指方向，有观点的给出这样的几个方面的大胆联想式的概述：0.明确背景和核心问题，并挖掘一些潜在的对于解决问题本身和个人不足之处的信息？1.当前状态是什么？2.产生这种状态的原因是什么？3.应该怎么做？4.可能面临的困难是什么？5.预测的结果如何？。"
    ]

    # 加载数据
    hexagrams = load_hexagram_data(hex_json_file_path)
    jiao_shi_data = load_jiao_shi_yi_lin_data(jiao_shi_json_file_path)

    # 检查数据加载
    if not hexagrams:
        print("错误：无法加载六十四卦数据，程序终止。")
        return
    if not jiao_shi_data:
        print("警告：无法加载焦氏易林数据，将无法显示焦氏易林解。")

    gender, _ = prompt_user_input(output)

    # 生成并规范化本卦
    primary_binary = generate_primary_hexagram_binary(gender)
    normalized_primary = normalize_hexagram_binary(primary_binary)

    # 显示本卦，获取动爻数和名称
    primary_moving_line, primary_name = display_hexagram(
        "本卦（占卜所问之事的当前状态）",
        normalized_primary, hexagrams, output, simplified, show_moving_info=True
    )

    changed_binary = None
    changed_name = None

    # 计算并显示变卦（如果本卦有效）
    if primary_moving_line is not None and primary_name is not None:
        changed_binary = compute_changed_hexagram(normalized_primary, primary_moving_line, simplified, output)

        if changed_binary:
            # 显示变卦，获取名称
            _, changed_name = display_hexagram(
                "变卦（占卜所问之事的预测结果）",
                changed_binary, hexagrams, output, simplified, show_moving_info=False # 变卦不显示动爻
            )

            # 查找并显示焦氏易林解
            if changed_name and jiao_shi_data:
                jiao_shi_entry = lookup_jiao_shi_yi_lin(primary_name, changed_name, jiao_shi_data)
                output.append("\n===== 焦氏易林解 =====")
                if jiao_shi_entry:
                    output.append(f"本卦：{jiao_shi_entry.get('本卦', primary_name)}")
                    output.append(f"变卦：{jiao_shi_entry.get('变卦', changed_name)}")
                    output.append(f"焦氏易林辞：{jiao_shi_entry.get('焦氏易林辞', '无')}")
                else:
                    output.append(f"未找到从 {primary_name} 到 {changed_name} 的焦氏易林记录。")
            elif not jiao_shi_data:
                 output.append("\n(焦氏易林数据未加载，无法提供此解)")

        else:
            output.append("\n错误：无法计算变卦。")

    else:
        output.append("\n错误：无法获取本卦的动爻或名称，无法继续生成变卦及后续卦象。")

    # 计算并显示其他卦象（如果本卦二进制有效）
    if len(normalized_primary) == 7:
        # 互卦: 上卦取本卦爻543 ([2:5]), 下卦取本卦爻432 ([1:4])
        mutual_inner_6bit = normalized_primary[2:5] + normalized_primary[1:4]
        mutual_binary = normalize_hexagram_binary('0' + mutual_inner_6bit)
        display_hexagram("互卦（占卜所问之事的内在原因）",
                         mutual_binary, hexagrams, output, simplified, show_moving_info=print_extra)

        # 错卦: 取本卦除符号位外的6爻逐位取反
        error_inner_6bit = ''.join('1' if bit == '0' else '0' for bit in normalized_primary[1:])
        error_binary = normalize_hexagram_binary('0' + error_inner_6bit)
        display_hexagram("错卦（占卜所问之事的应对策略）",
                         error_binary, hexagrams, output, simplified, show_moving_info=print_extra)

        # 综卦: 取本卦除符号位外的6爻上下逆序排列
        zong_inner_6bit = normalized_primary[1:][::-1]
        zong_binary = normalize_hexagram_binary('0' + zong_inner_6bit)
        display_hexagram("综卦（占卜所问之事的外在困难）",
                         zong_binary, hexagrams, output, simplified, show_moving_info=print_extra)
    elif primary_name is not None: # 仅在上面未报错时提示长度问题
        output.append("\n错误：本卦二进制长度异常，无法计算互、错、综卦。")


    # 保存结果到文件
    try:
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"question_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"\n占卜结果已保存到文件：{filename}")
    except Exception as e:
        print(f"\n错误：无法保存结果到文件 {filename}。错误信息: {e}")


# --- 主程序入口 ---
if __name__ == "__main__":
    # 执行占卜，传入两个数据文件路径
    perform_divination(HEXAGRAM_DATA_FILE, JIAO_SHI_DATA_FILE, simplified=True, print_extra=False)