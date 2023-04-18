# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
import json

with open('feihai_scheme.json','r',encoding='utf8')as fp:
    scheme_data = json.load(fp)
print(scheme_data.get("菲海战事")[1].get("夺取制海权")[0].get("action_model"))