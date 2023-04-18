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
current_path = os.path.abspath(os.path.dirname(__file__))

# 针对cmd命令行把mozi_ai_sdk的工程目录添加到sys.path（pycharm运行，不需要）
rootPath = current_path.partition('mozi_ai_sdk')[0]
sys.path.append(rootPath)

from mozi_ai_sdk.feihai_blue_ppo_v3_20221013.envs.env_feihai_blue import feihaiblue as Environment
# from mozi_ai_sdk.test.dppo.envs import env_remote as environment
from mozi_ai_sdk.feihai_blue_ppo_v3_20221013.envs import etc
from mozi_ai_sdk.dppo.utils.utils import print_arguments
from mozi_ai_sdk.feihai_blue_ppo_v3_20221013.PPO import PPO

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
flags.DEFINE_string("model_path", current_path + "\\bin\\checkpoints\\checkpoint-5000",
                    "Filepath to load initial model.")
flags.FLAGS(sys.argv)


def create_env():
    # if len(arg) != 1:
    #     # pdb.set_trace()
    #     env = environment.Environment(FLAGS.IP, FLAGS.Port, etc.DURATION_INTERVAL)
    # else:
    #     env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME,
    #                       etc.SIMULATE_COMPRESSION,
    #                       etc.DURATION_INTERVAL,
    #                       etc.SYNCHRONOUS)

    if FLAGS.platform_mode == 'versus':
        print('比赛模式')
        ip = FLAGS.IP
        port = FLAGS.Port
        env = Environment(ip, port, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION, etc.DURATION_INTERVAL,
                          etc.SYNCHRONOUS)

    else:
        print('开发模式')
        # env = Environment(etc.SERVER_IP, etc.SERVER_PORT)
        # env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION,
        #                   etc.DURATION_INTERVAL, etc.SYNCHRONOUS, etc.APP_MODE)
        env = Environment(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
                          etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                          platform_mode=FLAGS.platform_mode)

    env.start(etc.SERVER_IP, etc.SERVER_PORT)
    return env


def create_ppo_agent(env):
    # agent = PPOAgent(env=env, policy=policy, model_path=FLAGS.model_path)
    lr_actor = 0.0003  # learning rate for actor
    lr_critic = 0.001  # learning rate for critic
    gamma = 0.99  # discount factor
    K_epochs = 80  # update policy for K epochs
    eps_clip = 0.2  # clip parameter for PPO
    has_continuous_action_space = False
    action_std = None
    print('observation_space=',env.observation_space)
    print('action_space=', env.action_space)
    # env.observation_space = 740
    # env.observation_space = 330
    # env.observation_space = 338
    # env.action_space =71
    # env.action_space = 41
    # env.action_space = 56
    agent = PPO(env.observation_space, env.action_space, lr_actor, lr_critic, gamma, K_epochs, eps_clip, has_continuous_action_space, action_std)
    return agent


def evaluate():
    # 加载训练好的模型，直接评估
    total_test_episodes = 1  # total num of testing episodes
    max_ep_len = 1000
    env = create_env()
    env_name = 'feihai_blue'
    if FLAGS.agent == 'ppo':
        agent = create_ppo_agent(env)
    else:
        raise NotImplementedError

    try:
        random_seed = 0  #### set this to load a particular checkpoint trained on random seed
        run_num_pretrained = 0  #### set this to load a particular checkpoint num

        directory = "PPO_preTrained" + '/' + env_name + '/'
        checkpoint_path = directory + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("loading network from : " + checkpoint_path)

        agent.load(checkpoint_path)

        print("--------------------------------------------------------------------------------------------")

        test_running_reward = 0

        for ep in range(1, total_test_episodes + 1):
            ep_reward = 0
            state = env.reset()

            for t in range(1, max_ep_len + 1):
                # print('state=',state)
                # action = agent.select_action(state)
                if isinstance(state , tuple):
                    action = agent.select_action(state[0])
                else:
                    action = agent.select_action(state)
                state, reward, done= env.execute_action(action)
                ep_reward += reward

                if done:
                    break

            # clear buffer
            agent.buffer.clear()

            test_running_reward += ep_reward
            print('Episode: {} \t\t Reward: {}'.format(ep, round(ep_reward, 2)))
            ep_reward = 0

        # env.close()

        print("============================================================================================")

        avg_test_reward = test_running_reward / total_test_episodes
        avg_test_reward = round(avg_test_reward, 2)
        print("average test reward : " + str(avg_test_reward))

        print("============================================================================================")
    except KeyboardInterrupt:
        pass
    # finally:
    #     env.close()

def train():
    # 训练智能体
    env = create_env()
    if FLAGS.agent == 'ppo':
        agent = create_ppo_agent(env)
    else:
        raise NotImplementedError

    try:
        run_num_pretrained = 0  #### change this to prevent overwriting weights in same env_name folder
        random_seed = 0  # set random seed if required (0 = no random seed)
        env_name = 'feihai_blue'
        directory = "PPO_preTrained"
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = directory + '/' + env_name + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        checkpoint_path = directory + "PPO_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("save checkpoint path : " + checkpoint_path)
        if os.path.exists(checkpoint_path):
            print('加载训练好的模型继续训练')
            agent.load(checkpoint_path)
        log_dir = "PPO_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_dir = log_dir + '/' + env_name + '/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        #### get number of log files in log directory
        run_num = 0
        current_num_files = next(os.walk(log_dir))[2]
        run_num = len(current_num_files)

        #### create new log file for each run
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
        max_training_timesteps = int(2e6)
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

            state = env.reset()
            current_ep_reward = 0

            for t in range(1, max_ep_len + 1):

                # select action with policy
                # print('state=',state)
                # print('state_dim=',state.shape)
                if isinstance(state , tuple):
                    action = agent.select_action(state[0])
                else:
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
def main(argv):
    logging.set_verbosity(logging.ERROR)
    # print_arguments(FLAGS)
    # evaluate()
    train()


if __name__ == '__main__':
    app.run(main)
