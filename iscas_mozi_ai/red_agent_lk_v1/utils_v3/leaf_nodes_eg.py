# by aie

import random
import re
from time import time

import numpy as np 
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
from .utils import get_airs_centers


from .tools import *

import logging

random.seed(0)

lst = [
    '闪电 #5', '闪电 #6', '闪电 #7', '闪电 #8', '闪电 #9', '闪电 #10', '闪电 #11', '闪电 #12',
    '闪电 #13', '闪电 #14', '闪电 #15', '闪电 #16'
]

# lk add,2022-05-12
attack_air_lst = [
    '米格-29 #1', '米格-29 #2', '米格-29 #3', '米格-29 #4', '米格-29 #5', '米格-29 #6',
    '米格-29 #7', '米格-29 #8', '米格-29 #9', '米格-29 #10'
]

awac_air_list = ['卡-29 #7', '卡-29 #8', '卡-29 #9', '卡-29 #10']




def attack_condition_check(side_name, scenario):
    """
    11分钟后开始猎杀预警机和干扰机
    """
    side = scenario.get_side_by_name('蓝方')
    airs = side.aircrafts
    # 想定开始时间
    m_StartTime = scenario.m_StartTime
    # 当前时间
    m_Time = scenario.m_Time
    logging.info("当前时间：{}".format(m_Time))
    if m_Time - m_StartTime >= 660 and m_Time - m_StartTime <= 1000:
        for k, v in airs.items():
            if "EC-130H" in v.strName or "E-2K" in v.strName:
                # logging.info(f'{v.dLatitude},{v.dLongitude}')
                # import time
                # time.sleep(5)
                return True
            
        else:
            return False
    else:
        return False


def create_attack_mission(side_name, scenario):
    logging.info('创建打击任务...')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts

    attack_airs = {}
    num = 0
    for k, v in airs_dic.items():
        if num == 3:
            break
        if v.get_status_type in ["validToFly", 'InAir']:
            attack_airs[k] = v
        num += 1

    pass


def update_patrol_mission_v2(side_name, scenario):
    ''' 更新巡逻任务 '''
    logging.info("开始更新巡逻任务...s")
    side = scenario.get_side_by_name(side_name)
    # 巡逻任务1,2飞机飞行的路线设置的航路点
    xl1_lat = 0
    xl2_lat = 0
    # 参考点
    for point in side.referencepnts.values():
        if point.strName == side_name + 'rp2':
            xl1_lat = point.dLatitude
        elif point.strName == side_name + 'rp6':
            xl2_lat = point.dLatitude
    airs_dic = side.aircrafts

    ships_dic = side.ships

    # 想定开始时间
    m_StartTime = scenario.m_StartTime
    # 当前时间
    m_Time = scenario.m_Time
    # print(f'm_StartTime = {m_StartTime}')
    # print(f'm_Time = {m_Time}')
    # 执行任务的飞机,
    airs = {
        k: v
        for k, v in airs_dic.items() if int(re.sub('\D', '', v.strName)) >= 0
    }
    airs_name = [v.strName for v in airs_dic.values()]
    logging.info(f"执行巡逻任务飞机：{airs_name}")
    # 获取巡逻任务，如果巡逻任务为0，说明还没有，创建巡逻任务。
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    if len(patrol_missions) == 0:
        return False

    # 设置警戒区
    # alert_point_str = create_alert_zone(side_name, scenario)
    # 如果有任务，就每个任务更新，包含给任务分配飞机，1/3规则
    for patrol_mission in patrol_missions:
        # patrol_mission.set_prosecution_zone(alert_point_str)
        if patrol_mission.strName == side_name + 'xl_1':
            # 获取条令
            doctrine_xl1 = patrol_mission.get_doctrine()
            # '2002'-任务武器已耗光.允许使用航炮对临机目标进行打击（推荐）,
            doctrine_xl1.set_weapon_state_for_aircraft(2002)
            airs_xl1 = {
                k: airs[k]
                for k, v in airs.items() if v.strName in attack_air_lst[:4]
            }
            patrol_mission.assign_units(airs_xl1)

            # 设置任务编队规模
            patrol_mission.set_flight_size(2)
            # 如果任务没有设置航线，就添加航线

        if patrol_mission.strName == side_name + 'xl_2':
            if m_Time - m_StartTime >= 600:

                doctrine_xl2 = patrol_mission.get_doctrine()
                doctrine_xl2.set_weapon_state_for_aircraft(2002)
                airs_xl2 = {
                    k: airs[k]
                    for k, v in airs.items()
                    if v.strName in attack_air_lst[4:7]
                }
                patrol_mission.assign_units(airs_xl2)
                # 设置任务编队规模
                patrol_mission.set_flight_size(2)

        # 预警机
        if patrol_mission.strName == side_name + 'xl_3':
            doctrine_xl3 = patrol_mission.get_doctrine()
            doctrine_xl3.set_weapon_state_for_aircraft(2002)
            airs_xl3 = {
                k: airs[k]
                for k, v in airs.items() if v.strName in awac_air_list[:2]
            }
            patrol_mission.assign_units(airs_xl3)
            # 设置任务编队规模
            patrol_mission.set_flight_size(1)

        # 预警机
        if patrol_mission.strName == side_name + 'xl_4':
            doctrine_xl4 = patrol_mission.get_doctrine()
            doctrine_xl4.set_weapon_state_for_aircraft(2002)
            airs_xl4 = {
                k: airs[k]
                for k, v in airs.items() if v.strName in awac_air_list[2:]
            }
            patrol_mission.assign_units(airs_xl4)
            patrol_mission.set_flight_size(1)
        # 战斗机
        if patrol_mission.strName == side_name + 'xl_5':
            # if m_Time - m_StartTime >= 900:
            doctrine_xl5 = patrol_mission.get_doctrine()
            doctrine_xl5.set_weapon_state_for_aircraft(2002)
            airs_xl5 = {
                k: airs[k]
                for k, v in airs.items() if v.strName in attack_air_lst[7:]
            }
            patrol_mission.assign_units(airs_xl5)
            # 设置任务编队规模
            patrol_mission.set_flight_size(2)

        # 舰船海上控制巡逻
        if patrol_mission.strName == side_name + 'xl_6':
            doctrine_xl5 = patrol_mission.get_doctrine()
            doctrine_xl5.set_weapon_state_for_aircraft(2002)
            # airs_xl5 = {k: airs[k] for k, v in airs.items() if v.strName in attack_air_lst[7:]}
            patrol_mission.assign_units(ships_dic)
            # for air in airs_xl4.values():
            #     evade_ship(geopoint_target, air, doctrine_xl4)
    update_patrol_zone(side_name, scenario)
    return False


# 创建巡逻任务，红方米格-29
def create_patrol_mission(side_name, scenario):
    ''' 创建巡逻任务 '''
    logging.info("开始创建巡逻任务")
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    patrol_missions_dic = side.get_patrol_missions()
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}巡逻任务已创建')
    if flag == 'Yes':
        return False
    airs_c = [
        v for v in airs_dic.values() if int(re.sub('\D', '', v.strName)) < 11
    ]
    # print(airs_c)
    patrol_mission_name = [
        mission.strName for mission in patrol_missions_dic.values()
    ]
    logging.info(patrol_mission_name)
    # 根据驱逐舰的坐标，确定巡逻区参考点，根据巡逻区参考点，创建巡逻区
    point_list = create_patrol_zone(side_name, scenario)
    alert_point_str = create_alert_zone(side_name, scenario)

    # side = scenario.get_side_by_name(side_name)
    ships = side.ships
    for k, v in ships.items():
        if '舰' in v.strName:
            doctrine = v.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
            doctrine.set_em_control_status('Radar', 'Active')
    i = 1
    for point in point_list:
        point_str = []
        for name in point:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + 'xl_' + str(i)
        # 更新巡逻任务,给巡逻任务添加移动后的参考位点。
        if patrol_name in patrol_mission_name:
            for patrol in patrol_missions_dic.values():
                if patrol_name == patrol.strName:
                    patrol.set_patrol_zone(point_str)
        else:
            if i == 6:
                patrolmssn = side.add_mission_patrol(patrol_name, 6, point_str)
                patrolmssn.set_flight_size_check('false')
            else:
                # 创建巡逻任务，设置1/3规则
                patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str)
                patrolmssn.set_prosecution_zone(alert_point_str)
                # dd_prosecution_zone
                # patrolmssn.set_one_third_rule('true')
                patrolmssn.set_flight_size_check('false')

        i += 1
    scenario.mozi_server.set_key_value(f'{side_name}巡逻任务已创建', 'Yes')
    return False


def create_alert_zone(side_name, scenario):
    ''' 设置1个警戒区，2022/05/17,lk '''
    logging.info("======开始设置警戒区域")

    side = scenario.get_side_by_name(side_name)
    ships = side.ships
    point_list = []
    for k, v in ships.items():
        if '驱逐舰' in v.strName:
            lat, lon = v.dLatitude, v.dLongitude
            rp1 = side.add_reference_point(side_name + 'rp100', lat + 2,
                                           lon + 2)
            rp2 = side.add_reference_point(side_name + 'rp101', lat - 1,
                                           lon + 3)
            rp3 = side.add_reference_point(side_name + 'rp102', lat - 1,
                                           lon - 3)
            rp4 = side.add_reference_point(side_name + 'rp103', lat + 2,
                                           lon - 2)
            point_list.append([rp1, rp2, rp3, rp4])
    for point in point_list:
        point_str = []
        for name in point:
            point_str.append(name.strName)
    return point_str


# 巡逻区域经纬度的生成
def create_patrol_zone(side_name, scenario):
    ''' 设置巡逻区，2022/05/17,lk '''
    logging.info("======开始设置巡逻区域======")

    side = scenario.get_side_by_name(side_name)
    ships = side.ships
    point_list = []
    # 根据本方航空母舰的位置创建巡逻区xl_1，xl_2
    for k, v in ships.items():
        # lat: 纬度， lon：经度
        if '驱逐舰' in v.strName:
            lat, lon = v.dLatitude, v.dLongitude
            # xl_1
            rp1 = side.add_reference_point(side_name + 'rp1', lat + 1.2,
                                           lon + 1)
            rp2 = side.add_reference_point(side_name + 'rp2', lat + 1,
                                           lon + 1.5)
            rp3 = side.add_reference_point(side_name + 'rp3', lat + 0.6,
                                           lon + 1)
            rp4 = side.add_reference_point(side_name + 'rp4', lat + 1,
                                           lon + 0.5)
            point_list.append([rp1, rp2, rp3, rp4])
            # xl_2
            rp5 = side.add_reference_point(side_name + 'rp5', lat + 0.7,
                                           lon - 1)
            rp6 = side.add_reference_point(side_name + 'rp6', lat + 1,
                                           lon - 1.5)
            rp7 = side.add_reference_point(side_name + 'rp7', lat + 1.2,
                                           lon - 1)
            rp8 = side.add_reference_point(side_name + 'rp8', lat + 1,
                                           lon - 0.6)
            point_list.append([rp5, rp6, rp7, rp8])
            # xl_3，分配预警机
            rp13 = side.add_reference_point(side_name + 'rp13', lat + 0.25,
                                            lon - 1)
            rp14 = side.add_reference_point(side_name + 'rp14', lat + 0.15,
                                            lon - 0.5)
            rp15 = side.add_reference_point(side_name + 'rp15', lat, lon - 1)
            rp16 = side.add_reference_point(side_name + 'rp16', lat + 0.15,
                                            lon - 2)
            point_list.append([rp13, rp14, rp15, rp16])

            # xl_4，分配预警机
            rp23 = side.add_reference_point(side_name + 'rp23', lat + 0.25,
                                            lon + 1)
            rp24 = side.add_reference_point(side_name + 'rp24', lat + 0.15,
                                            lon + 0.5)
            rp25 = side.add_reference_point(side_name + 'rp25', lat, lon + 1)
            rp26 = side.add_reference_point(side_name + 'rp26', lat + 0.15,
                                            lon + 2)
            point_list.append([rp23, rp24, rp25, rp26])

            # xl_5 分配战斗机巡逻
            rp33 = side.add_reference_point(side_name + 'rp33', lat + 0.4,
                                            lon - 2)
            rp34 = side.add_reference_point(side_name + 'rp34', lat + 0.2,
                                            lon - 1)
            rp35 = side.add_reference_point(side_name + 'rp35', lat, lon - 2)
            rp36 = side.add_reference_point(side_name + 'rp36', lat + 0.2,
                                            lon - 3)
            point_list.append([rp33, rp34, rp35, rp36])

            # xl_6 海上控制巡逻

            rp43 = side.add_reference_point(side_name + 'rp43',
                                            lat + 4 * random.random(),
                                            lon - 2 * random.random())
            rp44 = side.add_reference_point(side_name + 'rp44',
                                            lat + 4 * random.random(),
                                            lon - 1 * random.random())
            point_list.append([rp43, rp44])

    contacts = side.contacts
    # 根据对方驱逐舰位置创建巡逻区 xl_5,再菲海战事这个想定下不会创建
    for contact in contacts.values():
        if '驱逐舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp9 = side.add_reference_point(side_name + 'rp9', lat1 + 0.7,
                                           lon1 - 0.5)
            rp10 = side.add_reference_point(side_name + 'rp10', lat1 + 0.7,
                                            lon1 + 0.5)
            rp11 = side.add_reference_point(side_name + 'rp11', lat1 - 0.7,
                                            lon1 + 0.5)
            rp12 = side.add_reference_point(side_name + 'rp12', lat1 - 0.7,
                                            lon1 - 0.5)
            point_list.append([rp9, rp10, rp11, rp12])
            # point_list = [[rp1, rp2, rp3, rp4],[rp5, rp6, rp7, rp8],[rp9, rp10, rp11, rp12]]
    return point_list


def update_patrol_zone(side_name, scenario):
    ''' 更新巡逻区域，2022/05/17,lk '''
    logging.info("==========更新巡逻区域==========")
    side = scenario.get_side_by_name(side_name)
    ships = side.ships

    blue_side = scenario.get_side_by_name('蓝方')
    blue_airs = blue_side.aircrafts

    blue_airs_locations = []
    for b_air in blue_airs.values():
        lat = b_air.dLatitude
        lon = b_air.dLongitude
        blue_airs_locations.append([lat,lon])
    blue_airs_locations = np.array(blue_airs_locations)
    # 高风险区域，以及飞机数量
    high_threat_center,air_num = get_airs_centers(blue_airs_locations)
    xl1_flag = False
    xl3_flag = False
    if air_num > 4 :
        # xl_1,随时待命提供支援
        side.set_reference_point(side_name + 'rp1', high_threat_center[0] + 1.2, high_threat_center[1] + 0.5)
        side.set_reference_point(side_name + 'rp2', high_threat_center[0] + 1, high_threat_center[1] + 1)
        side.set_reference_point(side_name + 'rp3', high_threat_center[0] + 0.6, high_threat_center[1] + 0.5)
        side.set_reference_point(side_name + 'rp4', high_threat_center[0] + 1, high_threat_center[1] + 0.2)
        xl1_flag = True

        # xl_3
        side.set_reference_point(side_name + 'rp13', lat + 0.25, lon - 1)
        side.set_reference_point(side_name + 'rp14', lat + 0.15, lon - 0.5)
        side.set_reference_point(side_name + 'rp15', lat, lon - 1)
        side.set_reference_point(side_name + 'rp16', lat + 0.15, lon - 2)
        xl3_flag = True

    contacts = side.contacts
    ec_130_flag = False
    e2k_flag = False
    for air in blue_airs.values():
        logging.info("air.strName = {}".format(air.strName))
        if 'EC-130H' in air.strName:
            logging.info(f'{air.strName}')
            lat1, lon1 = air.dLatitude, air.dLongitude
            side.set_reference_point(side_name + 'rp33', lat1 + 0.7,
                                     lon1 - 0.5)
            side.set_reference_point(side_name + 'rp34', lat1 + 0.7,
                                     lon1 + 0.5)
            side.set_reference_point(side_name + 'rp35', lat1 - 0.7,
                                     lon1 + 0.5)
            side.set_reference_point(side_name + 'rp36', lat1 - 0.7,
                                     lon1 - 0.5)
            ec_130_flag = True

        if 'E-2K' in air.strName:
            logging.info(f'{air.strName}')
            lat1, lon1 = air.dLatitude, air.dLongitude
            # xl_2，巡逻区域2
            side.set_reference_point(side_name + 'rp5', lat1 + 0.7, lon1 - 0.5)
            side.set_reference_point(side_name + 'rp6', lat1 + 0.7, lon1 + 0.5)
            side.set_reference_point(side_name + 'rp7', lat1 - 0.7, lon1 + 0.5)
            side.set_reference_point(side_name + 'rp8', lat1 - 0.7, lon1 - 0.5)
            e2k_flag = True

    
    # 根据本方航空母舰的位置创建巡逻区xl1，xl2
    for k, v in ships.items():
        # lat: 纬度， lon：经度
        if '驱逐舰' in v.strName:
            if not xl1_flag:
                lat, lon = v.dLatitude, v.dLongitude
                # xl1,随时待命提供支援
                side.set_reference_point(side_name + 'rp1', lat + 1.2, lon + 0.5)
                side.set_reference_point(side_name + 'rp2', lat + 1, lon + 1)
                side.set_reference_point(side_name + 'rp3', lat + 0.6, lon + 0.5)
                side.set_reference_point(side_name + 'rp4', lat + 1, lon + 0.2)
            # xl2
            if not e2k_flag:
                side.set_reference_point(side_name + 'rp5', lat + 0.7, lon - 1)
                side.set_reference_point(side_name + 'rp6', lat + 1, lon - 1.5)
                side.set_reference_point(side_name + 'rp7', lat + 1.2, lon - 1)
                side.set_reference_point(side_name + 'rp8', lat + 1, lon - 0.6)

            # xl3
            if not xl3_flag:
                side.set_reference_point(side_name + 'rp13', lat + 0.25, lon - 1)
                side.set_reference_point(side_name + 'rp14', lat + 0.15, lon - 0.5)
                side.set_reference_point(side_name + 'rp15', lat, lon - 1)
                side.set_reference_point(side_name + 'rp16', lat + 0.15, lon - 2)

            # xl_4，分配预警机
            side.set_reference_point(side_name + 'rp23', lat + 0.25, lon + 1)
            side.set_reference_point(side_name + 'rp24', lat + 0.15, lon + 0.5)
            side.set_reference_point(side_name + 'rp25', lat, lon + 1)
            side.set_reference_point(side_name + 'rp26', lat + 0.15, lon + 2)

            # xl_5
            if not ec_130_flag:
                side.set_reference_point(side_name + 'rp33', lat + 0.4,
                                         lon - 1)
                side.set_reference_point(side_name + 'rp34', lat + 0.2,
                                         lon - 0.5)
                side.set_reference_point(side_name + 'rp35', lat, lon - 1)
                side.set_reference_point(side_name + 'rp36', lat + 0.2,
                                         lon - 2)

            # xl_6，
            side.set_reference_point(side_name + 'rp43',
                                     lat + 4 * random.random(),
                                     lon - 2 * random.random())
            side.set_reference_point(side_name + 'rp44',
                                     lat + 4 * random.random(),
                                     lon - 1 * random.random())
    contacts = side.contacts
    # 根据对方空中目标更新巡逻区域位置
    for contact in contacts.values():
        if contact.m_ContactType == 0:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp9', lat1 + 0.7, lon1 - 0.5)
            side.set_reference_point(side_name + 'rp10', lat1 + 0.7,
                                     lon1 + 0.5)
            side.set_reference_point(side_name + 'rp11', lat1 - 0.7,
                                     lon1 + 0.5)
            side.set_reference_point(side_name + 'rp12', lat1 - 0.7,
                                     lon1 - 0.5)


def update_air_attack(side_name, scenario):
    ''' 更新空中截击任务 '''
    logging.info('======更新空中截击任务======')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airsOnMssn = {
        k: v
        for k, v in airs_dic.items()
        if v.strActiveUnitStatus.find('正在执行任务') > 0
    }

    airs = {
        k: v
        for k, v in airs_dic.items() if int(re.sub('\D', '', v.strName)) < 9
    }
    contacts = side.contacts
    if airsOnMssn.__len__() == 0:
        return False
    if len(contacts) == 0 or len(airs) == 0:
        return False

    mssnSitu = side.strikemssns
    strkmssn = [v for v in mssnSitu.values() if 'strike' in v.strName]
    if len(strkmssn) != 2:
        return False
    strkmssn_1 = [v for v in mssnSitu.values() if v.strName == 'strike1'][0]
    strkmssn_2 = [v for v in mssnSitu.values() if v.strName == 'strike2'][0]
    # 设置任务条令
    doctrine = strkmssn_1.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    # 3：是, 编组成员达到武器状态时离开编队返回基地
    if doctrine.m_WeaponStateRTB != 3:
        doctrine.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB
    if doctrine.m_GunStrafeGroundTargets != 1:
        doctrine.gun_strafe_for_aircraft('1')  # m_GunStrafeGroundTargets
        # 0：自杀式攻击，不返回基地
    if doctrine.m_BingoJokerRTB != 0:
        doctrine.set_fuel_state_for_air_group('0')  # m_BingoJokerRTB
        # 0， 对潜目标自由开火
    if doctrine.m_WCS_Submarine != 0:
        doctrine.set_weapon_control_status('weapon_control_status_subsurface',
                                           '0')
        # 0， 对海目标自由开火
    if doctrine.m_WCS_Surface != 0:
        doctrine.set_weapon_control_status('weapon_control_status_surface',
                                           '0')
        # 0， 对地目标自由开火
    if doctrine.m_WCS_Land != 0:
        doctrine.set_weapon_control_status('weapon_control_status_land', '0')
        # 0， 对空目标自由开火
    if doctrine.m_WCS_Air != 0:
        doctrine.set_weapon_control_status('weapon_control_status_air', '0')

    doctrine_2 = strkmssn_2.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    if doctrine_2.m_WeaponStateRTB != 3:
        doctrine_2.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB
    if doctrine_2.m_GunStrafeGroundTargets != 1:
        doctrine_2.gun_strafe_for_aircraft('1')  # m_GunStrafeGroundTargets
    if doctrine_2.m_BingoJokerRTB != 0:
        doctrine_2.set_fuel_state_for_air_group('0')  # m_BingoJokerRTB
    if doctrine_2.m_WCS_Submarine != 0:
        doctrine_2.set_weapon_control_status(
            'weapon_control_status_subsurface', '0')
    if doctrine_2.m_WCS_Surface != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_surface',
                                             '0')
    if doctrine_2.m_WCS_Land != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_land', '0')
    if doctrine_2.m_WCS_Air != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_air', '0')

    mssnSitu = side.strikemssns
    patrolmssn = side.patrolmssns
    target = {
        k: v
        for k, v in contacts.items() if v.strName in ['EC-130H', "E-2K"]
    }

    strkmssn = [v for v in mssnSitu.values() if v.strName == 'strike2'][0]
    strkPatrol = [
        v for v in patrolmssn.values() if v.strName == 'strikePatrol'
    ]

    # 获取任务执行单元
    missionUnits = strkmssn.m_AssignedUnits.split('@')
    create = False
    for unitGuid in missionUnits:
        retreat, retreatPos = utils.check_unit_retreat_and_compute_retreat_pos(
            side, unitGuid)
        if retreat == True:
            if len(strkPatrol) == 0 & create is False:
                pos = {
                    'latitude': list(target.values())[0].dLatitude,
                    'longitude': list(target.values())[0].dLongitude
                }
                point_list = utils.create_patrol_zone(side, pos)
                postr = []
                for point in point_list:
                    postr.append(point.strName)
                strikePatrolmssn = side.add_mission_patrol(
                    'strikePatrol', 0, postr)
                # 取消满足编队规模才能起飞的限制（任务条令）
                strikePatrolmssn.set_flight_size_check('false')
                utils.change_unit_mission(side, strkmssn, strikePatrolmssn,
                                          missionUnits)
                return False
            else:
                break
    return False
    pass


def create_air_attack(side_name, scenario):
    ''' 构建空中截击任务 '''
    logging.info('======构建空中截击任务======')
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    airs_dic = side.aircrafts

    # 获取反舰任务飞机 米格4，5，6，7
    airs = {
        k: v
        for k, v in airs_dic.items()
        if 3 <= int(re.sub('\D', '', v.strName)) < 7
    }
    # airs_2 = {
    #     k: v
    #     for k, v in airs_dic.items()
    #     if 5 <= int(re.sub('\D', '', v.strName)) < 7
    # }

    if len(contacts) == 0 or len(airs) == 0:
        return False
    # 等巡逻的飞机全部起飞后，打击任务创建，然后开始起飞
    airs_patrol = side.patrolmssns
    if not airs_patrol:
        return False

    targets = {
        k: v
        for k, v in contacts.items()
        if (('EC-130H' in v.strName) | ('E-2K' in v.strName))
    }
    target_1 = {k: v for k, v in contacts.items() if ('EC-130H' in v.strName)}
    target_2 = {k: v for k, v in contacts.items() if ('E-2K' in v.strName)}
    for k, v in targets.items():
        side.set_mark_contact(k, 'H')
    # 打击任务
    mssnSitu = side.strikemssns
    if {k: v
            for k, v in mssnSitu.items()
            if v.strName == 'strike1'}.__len__() == 0:
        strkmssn_1 = side.add_mission_strike('strike1', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_1.set_flight_size_check('false')
    else:
        return False
    for k, v in target_1.items():
        # 分配目标
        strkmssn_1.assign_unit_as_target(k)
    # 分配执行任务部队
    strkmssn_1.assign_units(airs)
    if {k: v
            for k, v in mssnSitu.items()
            if v.strName == 'strike2'}.__len__() == 0:
        strkmssn_2 = side.add_mission_strike('strike2', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_2.set_flight_size_check('false')
    else:
        return False
    for k, v in target_2.items():
        strkmssn_2.assign_unit_as_target(k)
    strkmssn_2.assign_units(airs)

    # 通过 ctrl +x 拿到航线设置的点
    # side.add_plan_way(0, 'strike1Way')
    # wayPointList1 = [{
    #     'latitude': '26.0979297169117',
    #     'longitude': '153.365146994643'
    # }, {
    #     'latitude': '26.3202842588887',
    #     'longitude': '156.042461903776'
    # }, {
    #     'latitude': '26.1944400170521',
    #     'longitude': '158.022842478336'
    # }]
    # for item in wayPointList1:
    #     side.add_plan_way_point('strike1Way', item['longitude'],
    #                             item['latitude'])
    # strkmssn_1.add_plan_way_to_mission(0, 'strike1Way')

    # wayPointList2 = [
    #     {
    #         'latitude': '25.2543871879078',
    #         'longitude': '153.238096612711'
    #     },
    #     # {'latitude': '22.1273995718291', 'longitude': '156.353268774315'},
    #     {
    #         'latitude': '25.0437456203838',
    #         'longitude': '156.012005422884'
    #     },
    #     {
    #         'latitude': '25.3555661789075',
    #         'longitude': '157.515723257979'
    #     }
    # ]
    # for item in wayPointList2:
    #     side.add_plan_way_point('strike2Way', item['longitude'],
    #                             item['latitude'])
    # strkmssn_2.add_plan_way_to_mission(0, 'strike2Way')
    return False
