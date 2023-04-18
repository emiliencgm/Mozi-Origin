import random


def gene_num(base, epsilon=0.5):
    if random.random() < epsilon:
        return base + random.randint(5) * 0.01
    else:
        return base
