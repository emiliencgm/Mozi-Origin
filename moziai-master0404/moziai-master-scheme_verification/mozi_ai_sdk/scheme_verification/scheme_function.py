# by aie


import re
from scheme_function_done import *
import json
'''
方案构成：完整战役->分成不同阶段->每个阶段的战役级任务->每个战役任务包含的战术级指令行动，
根据任务时间确定任务执行顺序，根据指令触发条件，执行指令
'''
with open('feihai_scheme_v2.json','r',encoding='utf8')as fp:
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



