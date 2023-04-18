# from bt_dev import main_versus
# from blue_test import main_versus

from multiprocessing import Process
from env.env import Environment
from env import etc
#
# from blue_agent_hk_v1.utils.bt_agent_antiship import CAgent as Blue_agent
from blue_agent_lj.utils_attack_skill.bt_agent_antiship import CAgent as Blue_agent
# from blue_agent_lj.utils_comprehensive_skill.bt_agent_antiship import CAgent as Blue_agent
from red_agent_zzh_v1.utils.bt_red_defence import ZZHAgent as Red_agent
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

parser = argparse.ArgumentParser()
parser.add_argument("--avail_ip_port", type=str, default='127.0.0.1:6060')
parser.add_argument("--platform_mode", type=str, default='eval')
# parser.add_argument("--side_name", type=str, default='蓝方')
parser.add_argument("--agent_key_event_file", type=str, default=None)


def main(env):
    env.start()
    agents = {"red": Red_agent(), "blue": Blue_agent()}
    # 重置函数，加载想定,拿到想定发送的数据
    env.scenario = env.reset()
    red_side = env.scenario.get_side_by_name('红方')
    agents['red'].init_bt(env, '红方', 0, '')
    try:
        agents['blue'].init_bt(env, '蓝方', 0, '')
    except:
        # 蓝方智能体初始化 ,hk
        agents['blue'].my_act_tree(env, '蓝方', 0, "")

    step_count = 0
    while True:
        env.step()

        with open('./scenarios.json', 'w+', encoding='utf-8') as f:
            json.dump(env.scenario.get_scenario_info(), f)
        agents['red'].update_bt('红方', env.scenario)
        agents['blue'].update_bt('蓝方', env.scenario)
        logging.info(f"")
        logging.info(
            f"推演步数：{step_count},红方得分：{red_side.iTotalScore}，蓝方得分：{-red_side.iTotalScore}"
        )
        step_count += 1
        if env.is_done():
            print("推演结束！")
            sys.exit(0)
            # break
        else:
            pass


if __name__ == "__main__":
    args = parser.parse_args()
    EPISODE_NUMS = 100

    process_list = []
    for i in range(EPISODE_NUMS):
        try:
            print(
                f"============================================第{i}场推演开始===================================================="
            )
            logging.info(
                f"============================================第{i}场推演开始===================================================="
            )

            env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM,
                              etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION,
                              etc.DURATION_INTERVAL, etc.SYNCHRONOUS,
                              etc.APP_MODE)
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
