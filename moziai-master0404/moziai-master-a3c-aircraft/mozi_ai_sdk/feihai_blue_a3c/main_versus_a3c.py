import torch
import torch.nn as nn
from utils import v_wrap, set_init, push_and_pull, record
import torch.nn.functional as F
import sys
import torch.multiprocessing as mp
import multiprocessing as mp
from shared_adam import SharedAdam
from absl import flags
from mozi_ai_sdk.feihai_blue_a3c.a3c_net_discrete import Net
from mozi_ai_sdk.feihai_blue_a3c.envs.env_feihai_blue import feihaiblue as Environment
from mozi_ai_sdk.feihai_blue_a3c.a3c_worker_train import Worker
from mozi_ai_sdk.feihai_blue_a3c.envs import etc
import gym
import os
os.environ['MOZIPATH'] = 'G:\\墨子平台\\Mozi\MoziServer\\bin'
UPDATE_GLOBAL_ITER = 5
GAMMA = 0.9
FLAGS = flags.FLAGS
flags.DEFINE_string("platform_mode", '开发', "模式")
flags.FLAGS(sys.argv)
def create_env():
    env = Environment(etc.SERVER_IP, etc.SERVER_PORT, None, etc.DURATION_INTERVAL, etc.app_mode,
                      etc.SYNCHRONOUS, etc.SIMULATE_COMPRESSION, etc.SCENARIO_NAME,
                      platform_mode=FLAGS.platform_mode)
    env.start(etc.SERVER_IP, etc.SERVER_PORT)
    return env

if __name__ == "__main__":
    env = create_env()
    N_S = env.observation_space
    N_A = env.action_space
    gnet = Net(N_S, N_A)        # global network
    gnet.share_memory()         # share the global parameters in multiprocessing
    opt = SharedAdam(gnet.parameters(), lr=1e-4, betas=(0.92, 0.999))      # global optimizer
    global_ep, global_ep_r, res_queue = mp.Value('i', 0), mp.Value('d', 0.), mp.Queue()

    # parallel training
    workers = [Worker(gnet, opt, global_ep, global_ep_r, res_queue, N_S, N_A, env) for _ in range(mp.cpu_count())]
    [w.start() for w in workers]
    res = []                    # record episode reward to plot
    while True:
        r = res_queue.get()
        if r is not None:
            res.append(r)
        else:
            break
    [w.join() for w in workers]