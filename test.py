l = [False,"aa",False,"fubuiv","djkbjhksfvb0","wdjkbjkv",False,False]
print(l.count(False))
for i in range(l.count(False)):
    idx = l.index(False)
    l.pop(idx)
    print(l)