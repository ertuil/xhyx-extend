import logging
from typing import Dict
from main import get_word_yx, read_single_word
import tqdm

single_word_dict: Dict[str, str] = {}
read_single_word("dict/flypy_n.json")

"""读取扩展词库文件，生成词典"""
count = 0
line_list = []
with open("dict/zhwiki.dict.yaml", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        if "\t" not in line:
            continue
        try:
            s1 = line.split("\t")
            w = s1[0]
            symbol = s1[1]
            if len(s1) < 3:
                freq = 1
            else:
                freq = int(s1[2])
            get_word_yx(w)
        except Exception as e:
            print(e)
            continue
        line_list.append(line)

with open("dict/zhwiki.simple.dict.yaml", "w", encoding="utf-8") as f:
    for line in line_list:
        f.write(line + "\n")
