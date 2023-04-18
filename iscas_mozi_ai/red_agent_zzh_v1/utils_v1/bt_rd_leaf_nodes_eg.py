import re
import random
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission

warning_team_1 = {"卡-29 #7", "卡-29 #8", "卡-29 #9", "卡-29 #10"}
# warning_team_2 = {"卡-29 #9", "卡-29 #10"}

# attack_we_team = {"米格-29 #1", "米格-29 #2"}

anti_air_team_1 = {"米格-29 #1", "米格-29 #2", "米格-29 #3", "米格-29 #4",
                   "米格-29 #5", "米格-29 #6", "米格-29 #7", "米格-29 #8",
                   "米格-29 #9", "米格-29 #10"}

# attack_f16_team_1 = {"米格-29 #3", "米格-29 #4"}
# attack_f16_team_2 = {"米格-29 #5", "米格-29 #6"}
# attack_f16_team_3 = {"米格-29 #7", "米格-29 #8"}
# attack_f16_team_4 = {"米格-29 #9", "米格-29 #10"}

enemy_facility = {"1号机场", "2号机场", "白云III型USA 160 P/L 2海洋监控卫星"}

warning_rp = [[21.0, 125.0], [19.0, 123.0], [17.5, 125.0], [19.0, 126.5]]  # 必须是float，int会创建失败（关键是不会提示啊，服了）

anti_air_patrol_rp = [[20.0, 122.0], [21.5, 121.0], [16.0, 122.5], [19.0, 127.5]]
anti_air_prosecution_rp = [[20.0, 121.0], [22.5, 121.0], [16.0, 123.5], [20.0, 127.5]]


def warning_patrol_condition(side_name, scenario):
    print("\n===>预警机巡逻任务<===")
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    we_air_num = 0
    for k, v in airs.items():
        if v.strName in warning_team_1:
            we_air_num += 1
    if we_air_num <= 0:
        print("Warning: 无可用预警机")
        return True
    else:
        print("存在{}架预警机".format(we_air_num))
        return False


def update_warning_patrol_mission(side_name, scenario):
    print("==>更新预警机巡逻任务")
    side = scenario.get_side_by_name(side_name)
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    print("预警巡逻任务开始更新")
    airs = side.aircrafts
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + '预警':
            expected_number = 2
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if len(mission_units) >= 2:
                print("已有", len(mission_units), "架预警机起飞")
                return True
            doctrine = patrol_mission.get_doctrine()
            doctrine.set_weapon_state_for_aircraft(4002)
            warning_airs = {}
            count = 0
            for k, v in airs.items():
                if v.strName in warning_team_1:
                    warning_airs[k] = v
                    count += 1
            taking_off = expected_number - len(mission_units)
            if len(warning_airs) >= taking_off:
                warning_team = dict(random.sample(warning_airs.items(), taking_off))
            else:
                warning_team = warning_airs
            patrol_mission.assign_units(warning_team)
            patrol_mission.set_flight_size(1)
            for air in warning_team.values():
                print(air.strName, end=", ")
                air.set_radar_shutdown(False)
            print("已起飞")
    return False


def create_warning_patrol_mission(side_name, scenario):
    print("==>创建预警机巡逻任务", end=" ")
    side = scenario.get_side_by_name(side_name)
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}预警巡逻任务已创建')
    if flag == 'Yes':
        print("无需创建")
        return True
    print("")
    point_list = []
    for i in range(len(warning_rp)):
        point = side.add_reference_point(side_name + 'rp' + str(i), warning_rp[i][0], warning_rp[i][1])
        point_list.append(point)
    point_str = []
    for name in point_list:
        point_str.append(name.strName)
    # 新建巡逻区名字
    patrol_name = side_name + '预警'
    # 创建巡逻任务，设置1/3规则
    patrol_mission = side.add_mission_patrol(patrol_name, 0, point_str)
    patrol_mission.set_one_third_rule('false')
    scenario.mozi_server.set_key_value(f'{side_name}预警巡逻任务已创建', 'Yes')
    return True


def anti_air_condition(side_name, scenario):
    print("\n===>防空巡逻任务<===")
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    contacts = side.contacts
    enemy_dic = {}
    for k, v in contacts.items():
        if v.strName not in enemy_facility:
            enemy_dic[k] = v
    fight_air_num = 0
    for k, v in airs.items():
        if v.strName in anti_air_team_1:
            fight_air_num += 1
    if fight_air_num <= 0:
        print("Warning: 无可用战斗机机")
        return True
    elif len(enemy_dic) == 0:
        print("未侦测到敌方战机")
        return True
    else:
        print("存在{}架战斗机，{}架敌机来袭".format(fight_air_num, len(enemy_dic)))
        return False


def update_anti_air_mission(side_name, scenario):
    print("==>更新防空巡逻任务")
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    enemy_dic = {}
    for k, v in contacts.items():
        if v.strName not in enemy_facility:
            enemy_dic[k] = v
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    print("防空巡逻任务开始更新")
    airs = side.aircrafts
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + '防空':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if len(mission_units) >= 5:
                print("已有", len(mission_units), "架战斗机起飞")
                return True
            doctrine = patrol_mission.get_doctrine()
            doctrine.set_weapon_state_for_aircraft(2001)
            anti_air_airs = {}
            count = 0
            for k, v in airs.items():
                if v.strName in anti_air_team_1:
                    anti_air_airs[k] = v
                    count += 1
            if len(anti_air_airs) <= 10:
                warning_team = anti_air_airs
            else:
                warning_team = dict(random.sample(anti_air_airs.items(), 10))
            patrol_mission.assign_units(warning_team)
            patrol_mission.set_flight_size(2)
            for air in warning_team.values():
                print(air.strName, end=", ")
                air.set_radar_shutdown(False)
            print("已起飞")
    return False


def create_anti_air_mission(side_name, scenario):
    print("==>创建防空巡逻任务", end=" ")
    side = scenario.get_side_by_name(side_name)
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}防空巡逻任务已创建')
    if flag == 'Yes':
        print("无需创建")
        return True
    print("")
    patrol_point_list = []
    for i in range(len(anti_air_patrol_rp)):
        point = side.add_reference_point(side_name + 'rp' + str(i+4), anti_air_patrol_rp[i][0], anti_air_patrol_rp[i][1])
        patrol_point_list.append(point)
    prosecution_point_list = []
    for i in range(len(anti_air_prosecution_rp)):
        point = side.add_reference_point(side_name + 'rp' + str(i+8), anti_air_prosecution_rp[i][0], anti_air_prosecution_rp[i][1])
        prosecution_point_list.append(point)
    patrol_point_str = []
    for name in patrol_point_list:
        patrol_point_str.append(name.strName)
    prosecution_point_str = []
    for name in prosecution_point_list:
        prosecution_point_str.append(name.strName)
    # 新建巡逻区名字
    patrol_name = side_name + '防空'
    # 创建巡逻任务，设置1/3规则
    patrol_mission = side.add_mission_patrol(patrol_name, 0, patrol_point_str)
    patrol_mission.set_one_third_rule('false')
    patrol_mission.set_prosecution_zone(prosecution_point_str)
    scenario.mozi_server.set_key_value(f'{side_name}防空巡逻任务已创建', 'Yes')
    return True




