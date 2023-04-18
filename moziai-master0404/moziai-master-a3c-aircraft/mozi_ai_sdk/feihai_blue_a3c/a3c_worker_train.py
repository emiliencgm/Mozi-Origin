import torch
import torch.nn as nn
from datetime import datetime
from absl import flags
from mozi_ai_sdk.feihai_blue_a3c.envs.env_feihai_blue import feihaiblue as Environment
from mozi_ai_sdk.feihai_blue_a3c.envs import etc
from utils import v_wrap, set_init, push_and_pull, record
from a3c_net_discrete import Net
import torch.nn.functional as F
import torch.multiprocessing as mp
from shared_adam import SharedAdam
import os

class Worker(mp.Process):
    def __init__(self, gnet, opt, global_ep, global_ep_r, res_queue, N_S, N_A, env):
        super(Worker, self).__init__()
        self.g_ep, self.g_ep_r, self.res_queue = global_ep, global_ep_r, res_queue
        self.gnet, self.opt = gnet, opt
        self.lnet = Net(N_S, N_A)           # local network
        self.env = env

    def run(self):
        run_num_pretrained = 0  #### change this to prevent overwriting weights in same env_name folder
        random_seed = 0  # set random seed if required (0 = no random seed)
        env_name = 'feihai_blue'
        directory = "A3C_preTrained"
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = directory + '/' + env_name + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        checkpoint_path = directory + "A3C_{}_{}_{}.pth".format(env_name, random_seed, run_num_pretrained)
        print("save checkpoint path : " + checkpoint_path)
        if os.path.exists(checkpoint_path):
            print('加载训练好的模型继续训练')
            self.gnet.load_state_dict(torch.load(checkpoint_path, map_location=lambda storage, loc: storage))

        log_dir = "A3C_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_dir = log_dir + '/' + env_name + '/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        current_num_files = next(os.walk(log_dir))[2]
        run_num = len(current_num_files)

        #### create new log file for each run
        log_f_name = log_dir + '/A3C_' + env_name + "_log_" + str(run_num) + ".csv"
        start_time = datetime.now().replace(microsecond=0)
        print("Started training at (GMT) : ", start_time)

        print("============================================================================================")

        # logging file
        log_f = open(log_f_name, "w+")
        log_f.write('episode,timestep,reward\n')
        time_step = 0
        i_episode = 0
        max_training_timesteps = int(1e6)
        max_ep_len = 1000
        update_timestep = max_ep_len * 4
        print_freq = max_ep_len * 10
        save_model_freq = int(1e5)
        log_freq = max_ep_len * 2
        log_running_reward = 0
        log_running_episodes = 0
        print_running_reward = 0
        print_running_episodes = 0

        while time_step <= max_training_timesteps:
            s = self.env.reset()
            buffer_s, buffer_a, buffer_r = [], [], []
            # ep_r = 0.
            current_ep_reward = 0
            for t in range(1, max_ep_len + 1):
                a = self.lnet.choose_action(v_wrap(s[None, :]))
                s_, r, done = self.env.execute_action(a)
                current_ep_reward += r
                buffer_a.append(a)
                buffer_s.append(s)
                buffer_r.append(r)
                time_step += 1
                if time_step % update_timestep == 0:  # update global and assign to local net
                    # sync
                    print('参数更新')
                    push_and_pull(self.opt, self.lnet, self.gnet, done, s_, buffer_s, buffer_a, buffer_r, GAMMA)
                    buffer_s, buffer_a, buffer_r = [], [], []

                if time_step % log_freq == 0:
                    # log average reward till last episode
                    log_avg_reward = log_running_reward / log_running_episodes
                    log_avg_reward = round(log_avg_reward, 4)

                    log_f.write('{},{},{}\n'.format(i_episode, time_step, log_avg_reward))
                    log_f.flush()

                    log_running_reward = 0
                    log_running_episodes = 0
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
                    torch.save(self.gnet.state_dict(), checkpoint_path)
                    print("model saved")
                    print("Elapsed Time  : ", datetime.now().replace(microsecond=0) - start_time)
                    print(
                        "--------------------------------------------------------------------------------------------")
                if done:  # done and print information
                    break
                s = s_
            print_running_reward += current_ep_reward
            print_running_episodes += 1

            log_running_reward += current_ep_reward
            log_running_episodes += 1

            i_episode += 1
        log_f.close()
        print("============================================================================================")
        end_time = datetime.now().replace(microsecond=0)
        print("Started training at (GMT) : ", start_time)
        print("Finished training at (GMT) : ", end_time)
        print("Total training time  : ", end_time - start_time)
        print("============================================================================================")
        self.res_queue.put(None)