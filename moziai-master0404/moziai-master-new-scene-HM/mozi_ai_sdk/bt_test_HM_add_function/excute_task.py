import json
import socket

import time
from threading import Thread

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


def run():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(60)
    host = '127.0.0.1'
    #host = socket.gethostname()
    port = 11223
    server.bind((host, port))  # 绑定端口

    server.listen(1)  # 监听
    my_thread = Thread(target=excute_task, args=(server, ))
    my_thread.start()
    while True:
        time.sleep(3)
        global my_data
        if my_data:
            for i in my_data.keys():
                task_data = my_data[i]
                if not task_data:
                    continue
                if task_data['type'] == "patrol":
                    pass
                elif task_data['type'] == "air_attack":
                    pass
                elif task_data['type'] == "ship_attack":
                    pass
            my_data = None
            print("执行一次任务")
        print("无任务")


if __name__ == "__main__":
    run()
