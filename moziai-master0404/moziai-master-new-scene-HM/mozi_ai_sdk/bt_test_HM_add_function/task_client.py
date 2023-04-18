#!/usr/bin/python
# -*- coding: UTF-8 -*-
# client客户端

from base64 import encode
import socket
import time
import json

MaxBytes = 1024 * 1024
host = '127.0.0.1'
port = 11223
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(30)
client.connect((host, port))

with open("G:\\刘健\moziai-master\\moziai-master-new-scene-HM\\mozi_ai_sdk\\bt_test_HM_add_function\\task_data.json",
          "r",
          encoding="utf-8") as fp:
    task_data = json.load(fp)
task_data = json.dumps(task_data)
sendBytes = client.send(bytes(task_data.encode('utf-8')))
# sendBytes = client.send("发送".encode())
# if sendBytes <= 0:
#     break
recvData = client.recv(MaxBytes)
print(recvData)
client.close()