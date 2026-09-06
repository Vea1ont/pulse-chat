lst = ["a", "b", "a"]
dct = {}
for i in lst:
    if not i in dct:
        dct[i] = 1
    else:
        dct[i] += 1
print(dct)