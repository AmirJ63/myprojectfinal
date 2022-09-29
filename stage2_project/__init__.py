import random
ps_klee = [p + 1 for p in range(4)]
ps_kandinsky = [p + 1 for p in range(4, 8)]
rnd = random.choice([ps_klee, ps_kandinsky])
print(rnd)