import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df = pd.read_csv('DQN_feihai_blue_log_all_3.csv')
ax = df.plot(x='episode',y='reward')
df.plot(x='episode',y='total_reward',ax=ax)
plt.savefig('reward_dueling_dqn_1_155.jpg')
