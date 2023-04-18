
# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： main_versus.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from mozi_ai_sdk.bt_test_HM_add_function.env.env import Environment
from mozi_ai_sdk.bt_test_HM_add_function.env import etc
from mozi_ai_sdk.bt_test_HM.utils.bt_agent_antiship import CAgent
from leaf_nodes_eg_add_function import *
import argparse
import sys
import os
import traceback
import json
import socket
import time
from threading import Thread

parser = argparse.ArgumentParser()
parser.add_argument("--avail_ip_port", type=str, default='127.0.0.1:6060')
# 比赛专用 Mozi Intelligent competition
parser.add_argument("--is_mic", type=bool, default=False)
parser.add_argument("--side_name", type=str, default='蓝方')
parser.add_argument("--agent_key_event_file", type=str, default=None)
parser.add_argument("--request_id", type=str, default='蓝方')

my_data: dict = None
def excute_task(server):
    MaxBytes = 1024 * 1024
    try:
        client, addr = server.accept()  # 等待客户端连接
        print(addr, " 连接上了")
        while True:
            # 等待客户端消息
            data = client.recv(MaxBytes)
            ###
            global my_data
            my_data = json.loads(data)
            if my_data:
                if my_data["quit"] == 1:
                    my_data = None
                    server.close()
            # task_type:指令种类。int：（1，空中巡逻）
            print(my_data)
            client.send("任务已执行".encode())
    except Exception as e:
        print(e)
    finally:
        server.close()  # 关闭连接
        print("连接已断开")

def run(env, side_name=None):
    """
       行为树运行的起始函数
       :param env: 墨子环境
       :param side_name: 推演方名称
       :return:
       """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(60)
    host = '127.0.0.1'
    # host = socket.gethostname()
    port = 11223
    server.bind((host, port))  # 绑定端口

    server.listen(1)  # 监听
    my_thread = Thread(target=excute_task, args=(server,))
    my_thread.start()

    if not side_name:
        side_name = '蓝方'
    # 连接服务器，产生mozi_server
    env.start()

    # 重置函数，加载想定,拿到想定发送的数据
    env.scenario = env.reset()
    side = env.scenario.get_side_by_name(side_name)

    # 实例化智能体
    agent = CAgent()
    # 初始化行为树
    agent.init_bt(env, side_name, 0, '')
    step_count = 0
    while True:
        env.step()
        agent.update_bt(side_name, env.scenario)
        # 更新动作
        # time.sleep(3)
        global my_data
        if my_data:
            for i in my_data.keys():
                task_data = my_data[i]
                if not task_data:
                    continue
                if task_data['type'] == "patrol":
                    create_patrol_mission(side_name, env.scenario, task_data)
                elif task_data['type'] == "air_attack":
                    create_antisurfaceship_mission_add_function(side_name, env.scenario, task_data)
                elif task_data['type'] == "ship_attack":
                    create_antisurfaceship_ship_mission_add_function(side_name, env.scenario, task_data)
            my_data = None
            print("执行一次任务")
        print("无任务")
        print(f"'推演步数：{step_count}")
        step_count += 1
        if env.is_done():
            print('推演已结束！')
            sys.exit(0)
        else:
            pass

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
        env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION,
                          etc.DURATION_INTERVAL, etc.SYNCHRONOUS, etc.APP_MODE)

    run(env)


if __name__ == '__main__':
  main()
# except Exception as e:
#     error_file = open(__file__.replace('main_versus.py', 'error.log'), 'w', encoding='utf-8')
#     exc_type, exc_value, exc_obj = sys.exc_info()
#     traceback.print_exc(file=error_file)
#     sys.exit()
