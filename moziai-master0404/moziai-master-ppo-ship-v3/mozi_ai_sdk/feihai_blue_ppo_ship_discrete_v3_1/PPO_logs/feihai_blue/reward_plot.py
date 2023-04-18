import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df = pd.read_csv('PPO_feihai_blue_log_15.csv')
df.plot(x='episode',y='reward')
plt.savefig('reward_ppo_801_1335.jpg')
