# 时间 ： 2020/7/20 17:13
# 作者 ： Dixit
# 文件 ： etc.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

import os

APP_ABSPATH = os.path.dirname(__file__)

#######################
SERVER_IP = "127.0.0.1"
SERVER_PORT = "6060"
PLATFORM = 'windows'
# SCENARIO_NAME = "bt_test.scen"  # 距离近，有任务
# SCENARIO_NAME = "海峡风暴-资格选拔赛.scen"  # 没有任务
# SCENARIO_NAME = "海峡风暴-最新 - 护航.scen"
SCENARIO_NAME = "海峡风暴-资格选拔赛-蓝方任务随机方案-给周国进测试.scen"
# SCENARIO_NAME = "菲海战事-仅蓝方有任务-v2.scen"

SIMULATE_COMPRESSION = 3
DURATION_INTERVAL = 5
SYNCHRONOUS = True

#######################
MAX_EPISODES = 5000
MAX_BUFFER = 1000000
MAX_STEPS = 30
#######################
# app_mode:
# 1--local windows train mode
# 2--local linux train mode
# 3--remote windows evaluate mode
# 4--local windows evaluate mode
app_mode = 1
#######################
TMP_PATH = "%s/%s/tmp" % (APP_ABSPATH, SCENARIO_NAME)
OUTPUT_PATH = "%s/%s/output" % (APP_ABSPATH, SCENARIO_NAME)

CMD_LUA = "%s/cmd_lua" % TMP_PATH
PATH_CSV = "%s/path_csv" % OUTPUT_PATH
MODELS_PATH = "%s/Models/" % OUTPUT_PATH
EPOCH_FILE = "%s/epochs.txt" % OUTPUT_PATH
#######################

TRANS_DATA = True
