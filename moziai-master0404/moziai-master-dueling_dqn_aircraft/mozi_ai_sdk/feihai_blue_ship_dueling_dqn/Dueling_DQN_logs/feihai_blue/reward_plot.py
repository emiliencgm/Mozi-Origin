import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df = pd.read_csv('DQN_feihai_blue_log_0.csv')
df.plot(x='episode',y='reward')
plt.savefig('reward_dueling_dqn_1_176.jpg')
