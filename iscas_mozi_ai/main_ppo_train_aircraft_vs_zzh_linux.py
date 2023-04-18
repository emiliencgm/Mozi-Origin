# from bt_dev import main_versus
# from blue_test import main_versus
from datetime import datetime
from multiprocessing import Process
from env.env import Environment
from blue_agent_lj.feihai_blue_ppo_v4_train_aircraft_zzh_linux.envs.env_feihai_blue import feihaiblue as Environment_train_air_zzh
# from blue_agent_lj.feihai_blue_ppo_test_v3.envs import etc
from blue_agent_lj.feihai_blue_ppo_v4_train_aircraft_zzh_linux.envs import etc_linux, etc
from blue_agent_lj.feihai_blue_ppo_v2_ship.PPO import PPO_ship
from blue_agent_lj.feihai_blue_ppo_v4_train_aircraft_zzh_linux.PPO import PPO
# from env import etc
#
# from blue_agent_hk_v1.utils.bt_agent_antiship import CAgent as Blue_agent
# from blue_agent_lj.utils_attack_skill.bt_agent_antiship import CAgent as Blue_agent
# from blue_agent_lj.utils_comprehensive_skill.bt_agent_antiship import CAgent as Blue_agent
from red_agent_zzh_v1.utils_v2.zzh_aggressive.z_ags_bt import ZAggressiveAgent as Red_agent
# from red_agent_lk_v1.utils.bt_agent_join_defence import CAgent as Red_agent
import argparse
import sys
import os
import traceback
import json

import logging

logging.basicConfig(format="【%(asctime)s】-【%(levelname)s】: %(message)s",
                    filename='run_zzh.log',
                    filemode='a',
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
    print('observation_space=',env.observation_space)
    print('action_space=', env.action_space)
    agent = PPO(env.observation_space, env.action_space, lr_actor, lr_critic, gamma, K_epochs, eps_clip, has_continuous_action_space, action_std)
    return agent


def main(env):
    env.start()
    agents = {"red": Red_agent()}
    env_name = 'feihai_blue'
    agent = create_ppo_agent(env)


    try:
        random_seed = 0  #### set this to load a particular checkpoint trained on random seed
        run_num_pretrained = 0  #### set this to load a particular checkpoint num

        directory = "blue_agent_lj" + '/' + "feihai_blue_ppo_v4_train_aircraft_zzh_linux" + '/' + "PPO_preTrained" + '/' + env_name + '/'
        checkpoint_path = directory + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path)

        agent.load(checkpoint_path)

        print('加载训练好的模型继续训练')

        log_dir = "blue_agent_lj" + '/' + "feihai_blue_ppo_v4_train_aircraft_zzh_linux" + '/' + "PPO_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_dir = log_dir + '/' + env_name + '/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_num_files = next(os.walk(log_dir))[2]
        run_num = len(current_num_files)
        log_f_name = log_dir + '/PPO_' + env_name + "_log_" + str(run_num) + ".csv"
        start_time = datetime.now().replace(microsecond=0)
        print("Started training at (GMT) : ", start_time)

        print("============================================================================================")

        # logging file
        log_f = open(log_f_name, "w+")
        log_f.write('episode,timestep,reward\n')

        # printing and logging variables
        print_running_reward = 0
        print_running_episodes = 0

        log_running_reward = 0
        log_running_episodes = 0

        time_step = 0
        i_episode = 0
        max_training_timesteps = int(1e6)
        max_ep_len = 500  # max timesteps in one episode
        update_timestep = max_ep_len * 4
        action_std_decay_rate = 0.05  # linearly decay action_std (action_std = action_std - action_std_decay_rate)
        min_action_std = 0.1  # minimum action_std (stop decay after action_std <= min_action_std)
        action_std_decay_freq = int(2.5e5)  # action_std decay frequency (in num timesteps)
        action_std = 0.6  # starting std for action distribution (Multivariate Normal)
        print_freq = max_ep_len * 10  # print avg reward in the interval (in num timesteps)
        log_freq = max_ep_len * 2  # log avg reward in the interval (in num timesteps)
        save_model_freq = int(1e5)  # save model frequency (in num timesteps)
        # training loop
        while time_step <= max_training_timesteps:
            print('9999999999999999999999999999999999999999999999999')
            env.scenario = env.reset()
            print('*******************************************')
            state = env.reset_ppo()
            red_side = env.scenario.get_side_by_name('红方')
            agents['red'].init_bt(env, '红方', 0, '')
            current_ep_reward = 0
            for t in range(1, max_ep_len + 1):
                env.step()
                agents['red'].update_bt('红方', env.scenario)
                # 这部分是打飞机的动作执行
                action = agent.select_action(state)
                state, reward, done = env.execute_action(action)
                # saving reward and is_terminals
                agent.buffer.rewards.append(reward)
                agent.buffer.is_terminals.append(done)

                time_step += 1
                current_ep_reward += reward

                # update PPO agent,train is on update
                if time_step % update_timestep == 0:
                    agent.update()

                # if continuous action space; then decay action std of ouput action distribution
                # if has_continuous_action_space and time_step % action_std_decay_freq == 0:
                #     agent.decay_action_std(action_std_decay_rate, min_action_std)

                # log in logging file
                if time_step % log_freq == 0:
                    # log average reward till last episode
                    log_avg_reward = log_running_reward / log_running_episodes
                    log_avg_reward = round(log_avg_reward, 4)

                    log_f.write('{},{},{}\n'.format(i_episode, time_step, log_avg_reward))
                    log_f.flush()

                    log_running_reward = 0
                    log_running_episodes = 0

                # printing average reward
                # 画reward图

                if time_step % print_freq == 0:
                    # print average reward till last episode
                    print_avg_reward = print_running_reward / print_running_episodes
                    print_avg_reward = round(print_avg_reward, 2)

                    print("Episode : {} \t\t Timestep : {} \t\t Average Reward : {}".format(i_episode, time_step,
                                                                                            print_avg_reward))

                    print_running_reward = 0
                    print_running_episodes = 0

                # save model weights
                if time_step % save_model_freq == 0:
                    print(
                        "--------------------------------------------------------------------------------------------")
                    print("saving model at : " + checkpoint_path)
                    agent.save(checkpoint_path)
                    print("model saved")
                    print("Elapsed Time  : ", datetime.now().replace(microsecond=0) - start_time)
                    print(
                        "--------------------------------------------------------------------------------------------")
                logging.info(f"")
                logging.info(
                    f"推演步数：{t},红方得分：{red_side.iTotalScore}，蓝方得分：{-red_side.iTotalScore}"
                )
                # break; if the episode is over
                if done:
                    break
            print_running_reward += current_ep_reward
            print_running_episodes += 1

            log_running_reward += current_ep_reward
            log_running_episodes += 1

            i_episode += 1
        log_f.close()
        # env.close()

        # print total training time
        print("============================================================================================")
        end_time = datetime.now().replace(microsecond=0)
        print("Started training at (GMT) : ", start_time)
        print("Finished training at (GMT) : ", end_time)
        print("Total training time  : ", end_time - start_time)
        print("============================================================================================")

    except KeyboardInterrupt:
        pass
    # finally:
    #     env.close()


if __name__ == "__main__":
    args = parser.parse_args()
    process_list = []

    # try:
        # env = Environment_all_v3(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
        #           etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
        #           platform_mode='开发')
        # env = Environment_train_air_zzh(etc_linux.SERVER_IP, etc_linux.SERVER_PORT, None, etc_linux.DURATION_INTERVAL, etc_linux.app_mode,
        #                          etc_linux.SYNCHRONOUS, etc_linux.SIMULATE_COMPRESSION, etc_linux.SCENARIO_NAME,
        #                          platform_mode='开发', platform="linux")
    env = Environment_train_air_zzh(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL,
                                    etc.app_mode,
                                    etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                                    platform_mode='开发')
        # p1 = Process(target=main, args=(env, ))
        # p1.start()
        # process_list.append(p1)
    main(env)
    # finally:
    #     for p in process_list:
    #         p.join()
