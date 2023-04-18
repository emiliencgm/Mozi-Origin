from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
from absl import app
from absl import flags
from absl import logging
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
current_path = os.path.abspath(os.path.dirname(__file__))
print('current_path=',current_path)

from mozi_ai_sdk.feihai_blue_ship_dueling_dqn.envs.env_feihai_blue_ship_dqn import feihaiblue_ship_dqn as Environment_ship_dqn
from mozi_ai_sdk.feihai_blue_ship_dueling_dqn.envs import etc
from mozi_ai_sdk.feihai_blue_ship_dueling_dqn.Dueling_DQN import DuelingDQN
from mozi_ai_sdk.feihai_blue_ship_dueling_dqn.utils import plot_learning_curve, create_directory

# 获取IP和Port
arg = sys.argv
print(arg)
# os.environ['MOZIPATH'] = 'D:\\mozi_server_个人版\\Mozi\\MoziServer\\bin'
os.environ['MOZIPATH'] = 'G:\\墨子平台\\Mozi\MoziServer\\bin'
FLAGS = flags.FLAGS
# flags.DEFINE_string("platform_mode", 'versus', "模式") # 'versus'
flags.DEFINE_string("platform_mode", '开发', "模式") # 'versus'
flags.DEFINE_integer("max_episodes", 5000, "Number of episodes to evaluate.")
flags.DEFINE_string("ckpt_dir", current_path + "\\checkpoints\\DuelingDQN\\",
                    "Filepath to load initial model.")
flags.DEFINE_string("reward_path", current_path + "\\output_images\\reward.png\\",
                    "Filepath to reward")
flags.DEFINE_string("epsilon_path", current_path + "\\output_images\\epsilon.png\\",
                    "Filepath to epsilon")
flags.FLAGS(sys.argv)


def create_env():
    print('开发模式')
    env = Environment_ship_dqn(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
                      etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                      platform_mode=FLAGS.platform_mode)

    env.start(etc.SERVER_IP, etc.SERVER_PORT)
    return env


def create_dqn_agent(env):
    agent = DuelingDQN(alpha=0.0003, state_dim=env.observation_space_ship, action_dim=env.action_space_ship,
                       fc1_dim=256, fc2_dim=256, ckpt_dir=FLAGS.ckpt_dir, gamma=0.99, tau=0.005, epsilon=1.0,
                       eps_end=0.05, eps_dec=5e-4, max_size=1000000, batch_size=256)
    return agent


def evaluate():
    # 加载训练好的模型，直接评估
    pass

def train():
    # 训练智能体
    env = create_env()
    agent = create_dqn_agent(env)
    env_name = 'feihai_blue'
    log_dir = "Dueling_DQN_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_dir = log_dir + '/' + env_name + '/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    current_num_files = next(os.walk(log_dir))[2]
    run_num = len(current_num_files)
    log_f_name = log_dir + '/DQN_' + env_name + "_log_" + str(run_num) + ".csv"
    log_f = open(log_f_name, "w+")
    log_f.write('episode,reward\n')
    try:
        create_directory(FLAGS.ckpt_dir, sub_dirs=['Q_eval', 'Q_target'])
        total_rewards, avg_rewards, eps_history = [], [], []
        if os.path.exists(FLAGS.ckpt_dir):
            print('加载训练好的模型继续训练')
            agent.load_models(150)
        for episode in range(FLAGS.max_episodes):
            # if os.path.exists(FLAGS.ckpt_dir):
            #     print('加载训练好的模型继续训练')
            #     agent.load_models(checkpoint_path)
            total_reward = 0
            done = False
            observation = env.reset()
            while not done:
                action = agent.choose_action(observation, isTrain=True)
                observation_, reward, done = env.execute_action(action)
                agent.remember(observation, action, reward, observation_, done)
                agent.learn()
                total_reward += reward
                observation = observation_

            total_rewards.append(total_reward)
            avg_reward = np.mean(total_rewards[-100:])
            avg_rewards.append(avg_reward)
            eps_history.append(agent.epsilon)
            print('EP:{} reward:{} avg_reward:{} epsilon:{}'.
                  format(episode + 1, total_reward, avg_reward, agent.epsilon))
            log_f.write('{},{}\n'.format(episode + 1, round(avg_reward, 1)))
            log_f.flush()

            if (episode + 1) % 50 == 0:
                agent.save_models()

        episodes = [i for i in range(FLAGS.max_episodes)]
        plot_learning_curve(episodes, avg_rewards, 'Reward', 'reward', FLAGS.reward_path)
        plot_learning_curve(episodes, eps_history, 'Epsilon', 'epsilon', FLAGS.epsilon_path)
        log_f.close()
    except KeyboardInterrupt:
        pass
def main(argv):
    logging.set_verbosity(logging.ERROR)
    # print_arguments(FLAGS)
    # evaluate()
    train()


if __name__ == '__main__':
    app.run(main)
