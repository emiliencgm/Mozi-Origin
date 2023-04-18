# s=[1,2,3]
# s1=[2,3,4]
# s2=[3,4,5]
# b=list(map(lambda x,y,z:x*y*z,s,s1,s2))
# print(b)
from itertools import product

# for a,b,c in product([10,2],[23,45],[1, 3]):
# #     print(a, b, c)
# import uuid
#
# # make a UUID based on the host address and current time
# uuidOne = uuid.uuid1()
# print ("Printing my First UUID of version 1")
# print(uuidOne)
import numpy as np
# a = np.array([3,3,3,3,3,3])
# print(a.shape)
# b=np.zeros((2,3))
# print(b)
# b[1,:] = [1,1,1]
# print(b)
a = np.load('./data_train/MAPPO_env_feihai_blue_number_1_seed_0.npy')
print(a)

for i in range(5):
    print('s')
print(i)