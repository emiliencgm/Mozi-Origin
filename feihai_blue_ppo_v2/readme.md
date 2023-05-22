# 强化学习智能体使用说明
1. 目录设置：将本文件夹放在`blue_agent_lj\moziai-master-ppo-aircraft\mozi_ai_sdk`目录下,**需要有与`mozi_ai_sdk`同级的`mozi_simu_sdk`才可运行**，`mozi_simu_sdk`为**华戍**墨子仿真模块，`mozi_ai_sdk`下每个文件夹是一个智能体，运行每个`mozi_ai_sdk`的**子文件夹**中的`main_versus.py`可运行每个智能体
2. `envs`文件夹中存储两个智能体的环境设计：`env_feihai_blue.py`RL学习巡逻任务的巡逻区；`env_feihai_blue_v2.py`RL学习飞机编队数量
3. 当前`main_versus.py`文件默认为运行`envs\env_feihai_blue_v2`RL学习飞机编队的数量，如果想要运行运行`env_feihai_blue.py`RL学习巡逻任务的巡逻区，修改`main_versus.py`import部分，注释掉17行，取消注释18行
4. 在命令行使用`tensorboard --logdir=PPO_reward`来观察TensorBoard实时反馈的模型奖励训练结果
5. 具体内容可见腾讯文档《墨子RL智能体代码理解辅助文档》