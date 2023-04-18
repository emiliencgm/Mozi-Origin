
import matplotlib.pyplot as plt
# 得到九宫格的9个坐标,0,10可以替换墨子的经纬度
import numpy as np
import random
a = []
start_lat = 22.3166521609224
start_lon = 121.148610750252
end_lat = 20.8166611844987
end_lon = 124.450782265488
for i in np.linspace(end_lat, start_lat, 4):
    for j in np.linspace(start_lon, end_lon, 4):
        a.append([i,j])
print(a)

index_list = []
for k in [0,1,2,4,5,6,8,9,10]:
    index_list.append([k,k+1,k+4,k+5])
print(index_list)
b = []
for m in index_list:
    c = []
    for n in m:
        c.append(a[n])
    b.append(c)
print(b)
k=random.choice(b)
print('k',k)
print(len(b))
# a=np.zeros((3,3))
# for i in range(3):
#     for j in range(3):
#         a[i,j] = random.randint(1,9)
# print(a)

