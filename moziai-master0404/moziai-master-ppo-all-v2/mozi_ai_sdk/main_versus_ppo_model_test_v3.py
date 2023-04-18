# 和v2的区别是打船任务变成反水面巡逻
# 20221018更好反水面巡逻的reward函数，更改反水面巡逻新模型
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
from absl import app
from absl import flags
from absl import logging
from datetime import datetime
import matplotlib.pyplot as plt
# current_path = os.path.abspath(os.path.dirname(__file__))
#
# # 针对cmd命令行把mozi_ai_sdk的工程目录添加到sys.path（pycharm运行，不需要）
# rootPath = current_path.partition('mozi_ai_sdk')[0]
# sys.path.append(rootPath)


from mozi_ai_sdk.feihai_blue_ppo_test_v3.envs.env_feihai_blue_all_v3 import feihaiblue_all_v3 as Environment_all_v3
from mozi_ai_sdk.feihai_blue_ppo_test_v3.envs import etc
from mozi_ai_sdk.feihai_blue_ppo_v2_ship.PPO import PPO_ship
from mozi_ai_sdk.feihai_blue_ppo_v2.PPO import PPO
# 获取IP和Port
arg = sys.argv
print(arg)
# os.environ['MOZIPATH'] = 'D:\\mozi_server_个人版\\Mozi\\MoziServer\\bin'
os.environ['MOZIPATH'] = 'G:\\墨子平台\\Mozi\MoziServer\\bin'
FLAGS = flags.FLAGS
# flags.DEFINE_string("platform_mode", 'versus', "模式") # 'versus'
flags.DEFINE_string("platform_mode", '开发', "模式") # 'versus'
flags.DEFINE_integer("num_episodes", 10, "Number of episodes to evaluate.")
flags.DEFINE_enum("agent", 'ppo', ['ppo', 'dqn', 'random', 'keyboard'],
                  "Agent name.")
flags.DEFINE_string("Side", "蓝方", "side info.")
flags.DEFINE_string("IP", "127.0.0.1", "server IP address.")
flags.DEFINE_string("Port", "6060", "port.")
flags.DEFINE_enum("policy", 'mlp', ['mlp', 'lstm'], "Job type.")
# flags.DEFINE_string("model_path", current_path + "\\checkpoints\\checkpoint", "Filepath to load initial model.")
# flags.DEFINE_string("model_path", current_path + "\\bin\\checkpoints\\checkpoint-5000",
#                     "Filepath to load initial model.")
flags.FLAGS(sys.argv)


def create_env():

    print('开发模式')
    env = Environment_all_v3(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
                      etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                      platform_mode=FLAGS.platform_mode)

    env.start(etc.SERVER_IP, etc.SERVER_PORT)
    return env

def create_ppo_agent(env):
    lr_actor = 0.0003  # learning rate for actor
    lr_critic = 0.001  # learning rate for critic
    gamma = 0.99  # discount factor
    K_epochs = 80  # update policy for K epochs
    eps_clip = 0.2  # clip parameter for PPO
    has_continuous_action_space = False
    action_std = None
    agent = PPO(env.observation_space, env.action_space, lr_actor, lr_critic, gamma, K_epochs, eps_clip, has_continuous_action_space, action_std)
    return agent

def create_ppo_agent_ship(env):
    # agent = PPOAgent(env=env, policy=policy, model_path=FLAGS.model_path)
    lr_actor = 0.0003  # learning rate for actor
    lr_critic = 0.001  # learning rate for critic
    gamma = 0.99  # discount factor
    K_epochs = 80  # update policy for K epochs
    eps_clip = 0.2  # clip parameter for PPO
    has_continuous_action_space = False
    action_std = None
    agent = PPO_ship(env.observation_space_ship, env.action_space_ship, lr_actor, lr_critic, gamma, K_epochs, eps_clip, has_continuous_action_space, action_std)
    return agent


def evaluate():
    # 加载训练好的模型，直接评估
    total_test_episodes = 1  # total num of testing episodes
    max_ep_len = 2000
    env = create_env()
    # env_ship = create_env_ship()
    env_name = 'feihai_blue'
    if FLAGS.agent == 'ppo':
        agent = create_ppo_agent(env)
        agent_ship = create_ppo_agent_ship(env)
    else:
        raise NotImplementedError

    try:
        random_seed = 0  #### set this to load a particular checkpoint trained on random seed
        run_num_pretrained = 0  #### set this to load a particular checkpoint num

        directory = "feihai_blue_ppo_test_v3" + '/' + "PPO_preTrained_aircraft" + '/' + env_name + '/'
        checkpoint_path = directory + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path)

        agent.load(checkpoint_path)

        directory_ship = "feihai_blue_ppo_test_v3" + '/' + "PPO_preTrained_ship" + '/' + env_name + '/'
        checkpoint_path_ship = directory_ship + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path_ship)
        agent_ship.load(checkpoint_path_ship)

        print("--------------------------------------------------------------------------------------------")

        test_running_reward_ship = 0
        test_running_reward = 0
        for ep in range(1, total_test_episodes + 1):
            ep_reward = 0
            state, state_ship = env.reset()
            ep_reward_ship = 0
            # state_ship = env_ship.reset()

            for t in range(1, max_ep_len + 1):
                # 这部分是打飞机的动作执行
                action = agent.select_action(state)
                state, reward = env.execute_action(action)
                ep_reward += reward

                # 这部分是打船的动作执行
                action_ship = agent_ship.select_action(state_ship)
                state_ship, reward_ship, done_ship= env.execute_action_ship(action_ship)
                ep_reward_ship += reward_ship

                if done_ship:
                    break

            # clear buffer
            agent.buffer.clear()
            agent_ship.buffer.clear()

            test_running_reward += ep_reward
            print('Episode: {} \t\t Reward: {}'.format(ep, round(ep_reward, 2)))
            test_running_reward_ship += ep_reward_ship
            print('Episode: {} \t\t Reward_Ship: {}'.format(ep, round(ep_reward_ship, 2)))
            ep_reward_ship = 0

        # env.close()

        print("============================================================================================")

        avg_test_reward = test_running_reward / total_test_episodes
        avg_test_reward = round(avg_test_reward, 2)
        print("average test reward : " + str(avg_test_reward))

        avg_test_reward_ship = test_running_reward_ship / total_test_episodes
        avg_test_reward_ship = round(avg_test_reward_ship, 2)
        print("average test reward ship : " + str(avg_test_reward_ship))

        print("============================================================================================")
    except KeyboardInterrupt:
        pass
    # finally:
    #     env.close()

def main(argv):
    logging.set_verbosity(logging.ERROR)
    # print_arguments(FLAGS)
    evaluate()
    # train()


if __name__ == '__main__':
    app.run(main)
