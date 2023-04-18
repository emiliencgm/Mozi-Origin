# from bt_dev import main_versus
# from blue_test import main_versus

from multiprocessing import Process
from env.env import Environment
from blue_agent_lj.feihai_blue_ppo_test_v3.envs.env_feihai_blue_all_v3 import feihaiblue_all_v3 as Environment_all_v3
# from blue_agent_lj.feihai_blue_ppo_test_v3.envs import etc
from blue_agent_lj.feihai_blue_ppo_test_v3.envs import etc_linux, etc
from blue_agent_lj.feihai_blue_ppo_v2_ship.PPO import PPO_ship
from blue_agent_lj.feihai_blue_ppo_v2.PPO import PPO
# from env import etc
#
# from blue_agent_hk_v1.utils.bt_agent_antiship import CAgent as Blue_agent
# from blue_agent_lj.utils_attack_skill.bt_agent_antiship import CAgent as Blue_agent
# from blue_agent_lj.utils_comprehensive_skill.bt_agent_antiship import CAgent as Blue_agent
# from red_agent_zzh_v1.utils_v2.zzh_aggressive.z_ags_bt import ZAggressiveAgent as Red_agent
# from red_agent_lk_v1.utils.bt_agent_join_defence import CAgent as Red_agent
from red_agent_lk_v1.utils_v1.bt_agent_join_defence import CAgent as Red_agent
# from red_agent_lk_v1.utils_v2.bt_agent_join_defence import CAgent as Red_agent
# from red_agent_lk_v1.utils_v3.bt_agent_join_defence import CAgent as Red_agent
import argparse
import sys
import os
import traceback
import json

import logging
file_log = open('run_lk_v2.log', encoding="utf-8",mode="a")
logging.basicConfig(format="【%(asctime)s】-【%(levelname)s】: %(message)s",
                    stream=file_log,
                    datefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.DEBUG)
#  设置墨子安装目录下bin目录为MOZIPATH，程序会自动启动墨子
# os.environ['MOZIPATH'] = 'E:/work/mozi/Mozi/MoziServer/bin'
os.environ['MOZIPATH'] = 'G:\\墨子平台\\Mozi\MoziServer\\bin'
# os.environ['MOZIPATH'] = '/home/LinuxServer/bin'

parser = argparse.ArgumentParser()
parser.add_argument("--avail_ip_port", type=str, default='127.0.0.1:6060')
parser.add_argument("--platform_mode", type=str, default='eval')
# parser.add_argument("--side_name", type=str, default='蓝方')
parser.add_argument("--agent_key_event_file", type=str, default=None)

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


def main(env):
    env.start()
    agents = {"red": Red_agent()}
    # env.scenario = env.reset()
    # 重置函数，加载想定,拿到想定发送的数据
    # agents['red'].init_bt(env, '红方', 0, '')
    # red_side = env.scenario.get_side_by_name('红方')

    # 加载训练好的模型，直接评估
    total_test_episodes = 1  # total num of testing episodes
    max_ep_len = 2000
    env_name = 'feihai_blue'
    agent = create_ppo_agent(env)
    agent_ship = create_ppo_agent_ship(env)

    try:
        random_seed = 0  #### set this to load a particular checkpoint trained on random seed
        run_num_pretrained = 0  #### set this to load a particular checkpoint num

        directory = "blue_agent_lj" + '/' + "feihai_blue_ppo_test_v3" + '/' + "PPO_preTrained_aircraft" + '/' + env_name + '/'
        checkpoint_path = directory + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path)

        agent.load(checkpoint_path)

        directory_ship = "blue_agent_lj" + '/' + "feihai_blue_ppo_test_v3" + '/' + "PPO_preTrained_ship" + '/' + env_name + '/'
        checkpoint_path_ship = directory_ship + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path_ship)
        agent_ship.load(checkpoint_path_ship)

        print("--------------------------------------------------------------------------------------------")

        test_running_reward_ship = 0
        test_running_reward = 0
        for ep in range(1, total_test_episodes + 1):
            ep_reward = 0
            env.scenario = env.reset()
            state, state_ship = env.reset_ppo()
            red_side = env.scenario.get_side_by_name('红方')
            agents['red'].init_bt(env, '红方', 0, '')
            ep_reward_ship = 0
            for t in range(1, max_ep_len + 1):
                agents['red'].update_bt('红方', env.scenario)
                # 这部分是打飞机的动作执行
                action = agent.select_action(state)
                state, reward = env.execute_action(action)
                ep_reward += reward

                # 这部分是打船的动作执行
                action_ship = agent_ship.select_action(state_ship)
                state_ship, reward_ship, done_ship = env.execute_action_ship(action_ship)
                ep_reward_ship += reward_ship
                logging.info(f"")
                logging.info(
                    f"推演步数：{t},红方得分：{red_side.iTotalScore}，蓝方得分：{-red_side.iTotalScore}"
                )
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


if __name__ == "__main__":
    args = parser.parse_args()
    EPISODE_NUMS = 10

    process_list = []
    for i in range(EPISODE_NUMS):
        try:
            print(
                f"============================================第{i}场推演开始===================================================="
            )
            logging.info(
                f"============================================第{i}场推演开始===================================================="
            )

            # env = Environment_all_v3(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
            #           etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
            #           platform_mode='开发')
            # env = Environment_all_v3(etc_linux.SERVER_IP, etc_linux.SERVER_PORT, None, etc_linux.DURATION_INTERVAL, etc_linux.app_mode,
            #                          etc_linux.SYNCHRONOUS, etc_linux.SIMULATE_COMPRESSION, etc_linux.SCENARIO_NAME,
            #                          platform_mode='开发', platform="linux")
            env = Environment_all_v3(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL,
                                     etc.app_mode,
                                     etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                                     platform_mode='开发')
            p1 = Process(target=main, args=(env, ))
            p1.start()
            process_list.append(p1)
            # main(env)

        except Exception as e:
            error_file = open(f'error_{i}.txt', 'w', encoding='utf-8')
            exc_type, exc_value, exc_obj = sys.exc_info()
            traceback.print_exc(file=error_file)

            # sys.exit()
            pass
        finally:
            for p in process_list:
                p.join()
    file_log.close()
