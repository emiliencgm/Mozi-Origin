
# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： main_versus.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from mozi_ai_sdk.scheme_verification.env.env import Environment
from mozi_ai_sdk.scheme_verification.env import etc_linux
from mozi_ai_sdk.scheme_verification.env import etc
import argparse
import sys
import os
import traceback
from scheme_function_done_v2 import *
import json
parser = argparse.ArgumentParser()
parser.add_argument("--avail_ip_port", type=str, default='127.0.0.1:6060')
# 比赛专用 Mozi Intelligent competition
parser.add_argument("--is_mic", type=bool, default=False)
parser.add_argument("--side_name", type=str, default='蓝方')
parser.add_argument("--agent_key_event_file", type=str, default=None)
parser.add_argument("--request_id", type=str, default='蓝方')


def run(env, side_name=None):
    """
       行为树运行的起始函数
       :param env: 墨子环境
       :param side_name: 推演方名称
       :return:
       """
    if not side_name:
        side_name = '蓝方'
    # 连接服务器，产生mozi_server
    env.start()

    # 重置函数，加载想定,拿到想定发送的数据
    env.scenario = env.reset()
    side = env.scenario.get_side_by_name(side_name)

    # 实例化智能体
    step_count = 0
    with open('feihai_scheme_v2.json', 'r', encoding='utf8') as fp:
        scheme_data = json.load(fp)
    order_list = []
    for campaign_name in scheme_data.keys():
        for campaign_stage in scheme_data.get(campaign_name):
            for stage_name in campaign_stage.keys():
                for task in campaign_stage.get(stage_name):
                    for task_parameter in task.keys():
                        if task_parameter == 'action_model':
                            for order_dic in task.get(task_parameter):
                                order_list.append(order_dic)
    print(order_list)
    print((len(order_list)))
    j = 1
    # 初始时间戳
    start_time = env.scenario.get_current_time()
    while True:
        env.step()
        # 更新动作

        for i, order_one in enumerate(order_list):
            create_mozi_order(side_name, env.scenario, order_one, i + j)
            updata_mozi_order(side_name, env.scenario, order_one, start_time)
            j += 4
        print(f"'推演步数：{step_count},本方得分：{side.iTotalScore}")
        step_count += 1
        if env.is_done():
            print('推演已结束！')
            # sys.exit(0)
            break
        else:
            pass
    # total_score = side.iTotalScore
    # return total_score

def main():

    args = parser.parse_args()
    if args.is_mic:     # 比赛专用 Mozi Intelligent competition
        print('专项赛模式')
        ip_port = args.avail_ip_port.split(":")
        ip = ip_port[0]
        port = ip_port[1]
        # 是否传入决策步长需讨论
        env = Environment(ip, port, duration_interval=etc.DURATION_INTERVAL, app_mode=3,
                          agent_key_event_file=args.agent_key_event_file, request_id=args.request_id)
    else:
        # 设置墨子安装目录下bin目录为MOZIPATH，程序会跟进路径自动启动墨子
        # os.environ['MOZIPATH'] = "D:/Mozi/MoziServer/bin"
        os.environ['MOZIPATH'] = 'G:\\墨子平台\\Mozi\MoziServer\\bin'
        print('默认开发模式')
        # env = Environment(etc_linux.SERVER_IP, etc_linux.SERVER_PORT, etc_linux.PLATFORM, etc_linux.SCENARIO_NAME, etc_linux.SIMULATE_COMPRESSION,
        #                   etc_linux.DURATION_INTERVAL, etc_linux.SYNCHRONOUS, etc_linux.APP_MODE)
        env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME,
                          etc.SIMULATE_COMPRESSION,
                          etc.DURATION_INTERVAL, etc.SYNCHRONOUS, etc.APP_MODE)

    run(env)


# try:
#     main()
# except Exception as e:
#     error_file = open(__file__.replace('main_versus.py', 'error.log'), 'w', encoding='utf-8')
#     exc_type, exc_value, exc_obj = sys.exc_info()
#     traceback.print_exc(file=error_file)
#     sys.exit()
main()