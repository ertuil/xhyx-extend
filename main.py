import logging
from typing import Dict, List, Tuple
import json

MAX_EXTEND_FREQ = 40000
CLOVER_MIN_FREQ = 80000
DEFAULT_FREQ = 20000

sg_word_dict: Dict[str, List[Tuple[str, int]]] = {}
sg_symbol_dict: Dict[str, List[Tuple[str, int]]] = {}

extend_word_dict: Dict[str, int] = {}

single_word_dict: Dict[str, str] = {}

output_symbol_dict: Dict[str, List[Tuple[str, int]]] = {}
output_word_dict: Dict[str, List[Tuple[str, int]]] = {}


def read_xhyx_sogou(filename: str = "xhyx-sogou.txt"):
    """读取小鹤搜狗输入法词库文件，生成词典"""
    replace_dict = {"h,1=和": "h,1=好", "h,2=化": "h,2=和"}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line in replace_dict:
                line = replace_dict[line]
            try:
                s1 = line.split(",")
                s = s1[0]
                s2 = s1[1].split("=")
                i = int(s2[0])
                w = s2[1]
            except:
                continue

            if w in sg_word_dict:
                sg_word_dict[w].append((s, i))
            else:
                sg_word_dict[w] = [(s, i)]

            if s in sg_symbol_dict:
                sg_symbol_dict[s].append((w, i))
                sg_symbol_dict[s].sort(key=lambda x: x[1], reverse=False)
            else:
                sg_symbol_dict[s] = [(w, i)]

            if len(w) == 1 and "o" not in s:
                if w not in single_word_dict:
                    single_word_dict[w] = s


def read_extend(filename: str = "extend-word.txt"):
    """读取扩展词库文件，生成词典"""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                s1 = line.split("\t")
                w = s1[0]
                freq = int(s1[2])
            except:
                continue
            if freq > MAX_EXTEND_FREQ:
                continue
            extend_word_dict[w] = freq


def read_clover(filename: str = "clover.phrase.dict.yaml", max_freq: int = 45596467, min_freq: int = 100000):
    """读取扩展词库文件，生成词典"""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                s1 = line.split("\t")
                w = s1[0]
                freq = int(s1[2])
            except:
                continue
            if len(w) > 3:
                continue
            if freq < min_freq:
                continue
            if w in extend_word_dict:
                continue
            extend_word_dict[w] = (1 - freq / max_freq) * 56000


def read_single_word(filename: str = "flypy_n.json"):
    """读取单字词库文件，生成词典"""

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for elem in data:
        w: str = elem["character"]
        s_list: str = elem["fly_code"]
        s = s_list.split()[0]
        if len(s) > 4:
            s = s[:4]
        single_word_dict[w] = s


def get_word_yx(word: str) -> str:
    try:
        if len(word) == 1:
            return single_word_dict[word]
        if len(word) == 2:
            w1, w2 = word[0], word[1]
            p1 = single_word_dict[w1][:2]
            p2 = single_word_dict[w2][:2]
            return p1 + p2
        if len(word) == 3:
            w1, w2, w3 = word[0], word[1], word[2]
            p1 = single_word_dict[w1][0]
            p2 = single_word_dict[w2][0]
            p3 = single_word_dict[w3][:2]
            return p1 + p2 + p3
        if len(word) >= 4:
            w1, w2, w3, w4 = word[0], word[1], word[2], word[-1]
            p1 = single_word_dict[w1][0]
            p2 = single_word_dict[w2][0]
            p3 = single_word_dict[w3][0]
            p4 = single_word_dict[w4][0]
            return p1 + p2 + p3 + p4
        raise ValueError(f"Invalid word length ({word})")
    except Exception as e:
        raise ValueError(f"Invalid xhyx ({word}): {e}")


def parse_sg_list() -> List[Tuple[str, str, int, int]]:
    """解析单字词库"""
    sg_extend_list: List[Tuple[str, str, int, int]] = []

    for w, symbol_list in sg_word_dict.items():
        for s, i in symbol_list:
            if (
                len(w) == 1
                or i == 1
                or s[0] == "o"
                or "$" in w
                or "#" in w
                or len(s) != 4
            ):
                ### 1. 单字词
                ### 2. 词频为1
                ### 3. 以'o'开头（符号、表情等）
                ### 4. 含有'$'符号（特殊符号）
                ### 5. 词库中的编码不是4位
                ### 上述内容保留原样输出
                if w in output_word_dict:
                    output_word_dict[w].append((s, i))
                else:
                    output_word_dict[w] = [(s, i)]

                if s in output_symbol_dict:
                    output_symbol_dict[s].append((w, i))
                    output_symbol_dict[s].sort(key=lambda x: x[1])
                else:
                    output_symbol_dict[s] = [(w, i)]
            else:
                if w in extend_word_dict:
                    freq = extend_word_dict[w]
                else:
                    freq = DEFAULT_FREQ
                sg_extend_list.append((w, s, i, freq))

    return sg_extend_list


def parse_extend_list(
    sg_extend_list: List[Tuple[str, str, int, int]]
) -> List[Tuple[str, str, int, int]]:
    """解析扩展词库"""

    for w, freq in extend_word_dict.items():
        if w in output_word_dict:
            continue
        if len(w) >= 4:
            continue
        new = True
        for cw, _, _, _ in sg_extend_list:
            if w == cw:
                new = False
                break
        if new:
            try:
                s = get_word_yx(w)
            except Exception as e:
                logging.warning(f"Invalid xhyx: {w} {e}")
                continue
            sg_extend_list.append((w, s, 1000, freq))
    # 根据权重排序
    sg_extend_list.sort(key=lambda x: x[3])
    return sg_extend_list


def extend_single_char():
    """补充字典中没有的单字"""
    count = 0
    for w, s in single_word_dict.items():
        if w in output_word_dict:
            continue
        logging.debug(f"Extend single word {w}")
        count += 1
        if s not in output_symbol_dict:
            idx = 1
            output_symbol_dict[s] = [(w, idx)]
            output_word_dict[w] = [(s, idx)]
        else:
            idx = len(output_symbol_dict[s]) + 1
            output_symbol_dict[s].append((w, idx))
            output_word_dict[w] = [(s, idx)]
    logging.info(f"Extend single word total number: {count}")


def extend_word(word: str, symbol: str, idx: int, freq: int):
    """解析双字词库"""
    if word in output_word_dict:
        logging.warning(f"Word already exists: {word}")
        return

    if symbol not in output_symbol_dict:
        idx = 1
        output_symbol_dict[symbol] = [(word, idx)]
        output_word_dict[word] = [(symbol, idx)]
        logging.debug(f"extend word: {word} symbol: {symbol} idx: {idx}")
    else:
        ### 第一轮，补充非首位词录入办法
        idx = len(output_symbol_dict[symbol]) + 1
        if idx == 1:
            logging.warning(
                f"234234 {symbol} {word} {idx} {output_symbol_dict[symbol]}"
            )
        output_symbol_dict[symbol].append((word, idx))
        output_word_dict[word] = [(symbol, idx)]
        logging.debug(f"extend word: {word} symbol: {symbol} idx: {idx}")

        ### 第二轮，引入词语的辅助码
        if len(word) > 2:
            return
        w1 = word[-1]
        w2 = word[0]
        candidate_s_1 = []
        candidate_s_2 = []
        try:
            candidate_s_1.append(symbol + single_word_dict[w1][2])
            candidate_s_1.append(symbol + single_word_dict[w2][2])
            candidate_s_2.append(symbol + single_word_dict[w1][2:4])
            candidate_s_2.append(symbol + single_word_dict[w2][2:4])
        except Exception as e:
            logging.warning(f"Invalid xhyx: {word} {e}")

        skip = False
        for s in candidate_s_1:
            if s not in output_symbol_dict:
                skip = True
                idx = 1
                output_symbol_dict[s] = [(word, idx)]
            else:
                idx = len(output_symbol_dict[s]) + 1
                output_symbol_dict[s].append((word, idx))
            output_word_dict[word].append((s, idx))

            if idx == 1:
                break
            logging.debug(f"extend word: {word} symbol: {s} idx: {idx}")

        if not skip:
            for s in candidate_s_2:
                if s not in output_symbol_dict:
                    idx = 1
                    output_symbol_dict[s] = [(word, idx)]
                else:
                    idx = len(output_symbol_dict[s]) + 1
                    output_symbol_dict[s].append((word, idx))
                output_word_dict[word].append((s, idx))
                if idx == 1:
                    break
                logging.debug(f"extend word: {word} symbol: {s} idx: {idx}")
    # print(word, symbol, idx)


def format_and_output(output_dir: str = ""):
    """格式化输出"""
    symbols = list(output_symbol_dict.keys())
    symbols.sort()
    final_output_symbol_dict: Dict[str, Tuple[str, int]] = {}
    final_output_symbol_list: List[Tuple[str, str, int]] = []

    for symbol in symbols:
        word_list = output_symbol_dict[symbol]
        word_list.sort(key=lambda x: x[1])

        new_word_list = [(w, new_idx + 1) for new_idx, (w, idx) in enumerate(word_list)]
        final_output_symbol_dict[symbol] = new_word_list

        for w, idx in new_word_list:
            final_output_symbol_list.append((symbol, w, idx))

    logging.info(f"Output symbol list: total {len(final_output_symbol_list)} lines")
    output_sogou(final_output_symbol_list, output_dir+"/output_flypy_sogou.txt")
    output_baidu(final_output_symbol_list, output_dir+"/output_flypy_baidu.ini")


def output_sogou(
    final_output_list: List[Tuple[str, str, int]],
    filename: str = "output_flypy_sogou.txt",
):
    str_list = []
    for symbol, word, idx in final_output_list:
        str_list.append(f"{symbol},{idx}={word}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(str_list))


def output_baidu(
    final_output_list: List[Tuple[str, str, int]],
    filename: str = "output_flypy_baidu.ini",
):
    str_list = []
    for symbol, word, idx in final_output_list:
        if "$" in word or "#" in word:
            continue
        str_list.append(f"{symbol}={idx},{word}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(str_list))


def main():
    logging.basicConfig(level=logging.DEBUG)
    ## Step 1：读取内容
    ## 读取小鹤音形单字表
    read_single_word("dict/flypy_n.json")
    ## 读取官方搜狗词典
    read_xhyx_sogou("dict/xhyx-sogou.txt")
    ## 读取汉语常用词表
    read_extend("dict/extend-word.txt")
    read_clover("dict/clover.phrase.dict.yaml", 45596467, 200000)
    read_clover("dict/THUOCL_IT.dict.yaml", 395499, 1000)
    read_clover("dict/THUOCL_caijing.dict.yaml", 1934814, 200)
    read_clover("dict/sogou_network.dict.yaml", 2, 0)

    ## Step 2：整理扩展的词汇表
    extend_list = parse_sg_list()
    extend_list = parse_extend_list(extend_list)

    ## Step 3：补充不常见的字
    extend_single_char()

    ## Step 4：对非首位的词进行补充处理
    logging.info(f"Extend list: {len(extend_list)}")
    for w, s, i, freq in extend_list:
        extend_word(w, s, i, freq)

    ## Step 5：打印输出
    format_and_output("output")


if __name__ == "__main__":
    main()
