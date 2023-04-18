import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df = pd.read_excel('PPO_feihai_blue_log_all.xlsx')
df.plot(x='episode',y='reward')
plt.savefig('reward_ppo_1_609.jpg')
