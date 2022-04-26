prime = 31
rems = []
pow = 1
generator = 3
while len(rems) < prime-1:
    pow = pow*generator
    remain = pow % prime
    if remain not in rems:
        rems.append(remain)
        print("Added ${{1}} at value {2}", remain, pow)

# 11 and 2 | 23 and 5 | 31 and 3
