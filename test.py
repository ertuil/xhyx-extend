from pyshuangpin import shuangpin, Scheme
import pypinyin

hans = '长度 师长'
sp = shuangpin(hans, Scheme.小鹤, style=pypinyin.NORMAL)
print(sp)