#imports here
import random


rounds=6
x=2016
g=2
p=11
y = (g**x) % p

def zero_knowledge_proof(y, p, g, rounds):
    for i in range(0,rounds):
        r = random.randrange(0, p - 1, 1)
        h = (g ** r) % p
        b = random.randint(0, 1)
        s = (r + b*x)%(p-1)
        t = (g ** s) % p
        u = (h * (y ** b)) % p
        if t==u:
            return True
    return False
