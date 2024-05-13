from pyshuangpin import shuangpin, Scheme
import pypinyin

hans = '师长 军长 旅长'
sp = shuangpin(hans, Scheme.小鹤, style=pypinyin.NORMAL)
print(sp)