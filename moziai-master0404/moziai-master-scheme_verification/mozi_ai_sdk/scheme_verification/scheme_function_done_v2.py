# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
from feihai_config import MISSION_TYPE, ORDER_TYPE
import json
'''
方案构成：完整战役->分成不同阶段->每个阶段的战役级任务->每个战役任务包含的战术级指令行动，
根据任务时间确定任务执行顺序，根据指令触发条件，执行指令
警戒区没加
'''

def create_mozi_order(side_name, scenario, order_dic, i):
    if order_dic.get('order_type') == ORDER_TYPE.ADD_SUPPORT_ORDER:
        side = scenario.get_side_by_name(side_name)
        # 建立支援任务1,如果有了就不创建了
        support_missions_dic = side.get_support_missions()
        support_mission_name = [mission.strName for mission in support_missions_dic.values()]
        airs_dic = side.aircrafts

        support_rule = order_dic.get('order_rule')
        support_name = order_dic.get('order_name')
        if support_name not in support_mission_name:
            air_name = order_dic.get('unit_name')
            start_mission_time = order_dic.get('order_start_time')
            airs_support = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in air_name}
            supprot_zone = order_dic.get('support_zone')
            support_point_list = support_zone_for_two(side_name, scenario, supprot_zone, i)
            for point in support_point_list:
                point_str_support = []
                for name in point:
                    point_str_support.append(name.strName)
                supportmssn = side.add_mission_support(support_name, point_str_support)
                print('支援任务已创建')
                supportmssn.set_is_active('true')
                supportmssn.assign_units(airs_support)
                supportmssn.set_one_third_rule(support_rule.get('one_third_rule'))
                supportmssn.set_flight_size(support_rule.get('flight_size'))
                supportmssn.set_flight_size_check(support_rule.get('set_flight_size_check'))
                supportmssn.set_start_time(start_mission_time)

    # elif order_dic.get('order_type') == ORDER_TYPE.UPDATE_REFENCE_POINT:
    #     side = scenario.get_side_by_name(side_name)
    #     current_simtime = side.simulate_time
    #     print('current_simtime=', current_simtime)
    #     if current_simtime == order_dic.get('order_start_time'):
    #         old_refence_point_name_list = order_dic.get('old_support_zone_name')
    #         new_point_list = order_dic.get('new_support_zone')
    #         updata_zone(side_name, scenario, old_refence_point_name_list, new_point_list)

    elif order_dic.get('order_type') == ORDER_TYPE.ADD_AIR_PATROL_ORDER:
        side = scenario.get_side_by_name(side_name)
        patrol_missions_dic = side.get_patrol_missions()
        patrol_mission_name = [mission.strName for mission in patrol_missions_dic.values()]
        airs_dic = side.aircrafts
        patrol_rule = order_dic.get('order_rule')
        patrol_name = order_dic.get('order_name')
        if patrol_name not in patrol_mission_name:
            air_name = order_dic.get('unit_name')
            start_mission_time = order_dic.get('order_start_time')
            airs_patrol = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in air_name}
            prosecution_zone = order_dic.get('prosecution_zone')
            prosecution_zone_list = creat_prosecution_area(side_name, scenario, prosecution_zone, i)
            ps_str = []
            for ps in prosecution_zone_list:
                for name in ps:
                    ps_str.append(name.strName)
            patrol_zone = order_dic.get('patrol_zone')
            patrol_point_list = create_patrol_zone(side_name, scenario, patrol_zone, i)
            for point in patrol_point_list:
                point_str_patrol = []
                for name in point:
                    point_str_patrol.append(name.strName)
                patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str_patrol)
                print('xl任务已创建')
                patrolmssn.set_is_active('true')
                patrolmssn.assign_units(airs_patrol)
                patrolmssn.set_patrol_zone(point_str_patrol)
                patrolmssn.set_prosecution_zone(ps_str)
                patrolmssn.set_one_third_rule(patrol_rule.get('one_third_rule'))
                patrolmssn.set_flight_size(patrol_rule.get('flight_size'))
                patrolmssn.set_flight_size_check(patrol_rule.get('set_flight_size_check'))
                patrolmssn.set_opa_check(patrol_rule.get('opa_check'))
                patrolmssn.set_wwr_check(patrol_rule.get('wwr_check'))
                patrolmssn.set_emcon_usage(patrol_rule.get('emcon_usage'))
                patrolmssn.set_start_time(start_mission_time)
    elif order_dic.get('order_type') == ORDER_TYPE.ADD_SEA_STRIKE_ORDER:
        side = scenario.get_side_by_name(side_name)
        contacts = side.contacts
        strike_missions_dic = side.get_strike_missions()
        strike_mission_name = [mission.strName for mission in strike_missions_dic.values()]
        airs_dic = side.aircrafts
        strike_rule = order_dic.get('order_rule')
        strike_name = order_dic.get('order_name')
        if strike_name not in strike_mission_name:
            air_name = order_dic.get('unit_name')
            start_mission_time = order_dic.get('order_start_time')
            airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in air_name}
            strkmssn_1 = side.add_mission_strike(strike_name, 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_1.set_one_third_rule(strike_rule.get('one_third_rule'))
            strkmssn_1.set_flight_size(strike_rule.get('flight_size'))
            strkmssn_1.set_flight_size_check(strike_rule.get('set_flight_size_check'))
            targets = {k: v for k, v in contacts.items() for ship_name in order_dic.get('target') if ship_name in v.strName}
            for k, v in targets.items():
                # set_mark_contact设置目标对抗关系,H is 敌方
                side.set_mark_contact(k, 'U')
            for k, v in targets.items():
                strkmssn_1.assign_unit_as_target(k)
            strkmssn_1.assign_units(airs_strike)
            strike_plot_name = order_dic.get('strike_plot_name')
            strike_plot_point_list = order_dic.get('strike_plot_point')
            side.add_plan_way(0, strike_plot_name)
            for item in strike_plot_point_list:
                side.add_plan_way_point(strike_plot_name, item['longitude'], item['latitude'])
            strkmssn_1.add_plan_way_to_mission(0, strike_plot_name)
            strkmssn_1.set_start_time(start_mission_time)

def support_zone_for_two(side_name, scenario, support_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # latitude = '21.8764427622847', longitude = '121.330904108449'
    # latitude = '21.8335734773605', longitude = '121.478618597081'
    # latitude = '21.6920926322308', longitude = '121.580152213845'
    # latitude = '21.6899037180596', longitude = '121.405076571889'
    # point_1 = [(21.8764427622847, 121.330904108449), (21.8335734773605, 121.478618597081),
    #            (21.6920926322308, 121.580152213845), (21.6899037180596, 121.405076571889)]
    # print('support_zone=',support_zone)
    rp15 = side.add_reference_point(side_name + str(i + 0), support_zone[0][0], support_zone[0][1])
    rp16 = side.add_reference_point(side_name + str(i + 1), support_zone[1][0], support_zone[1][1])
    rp17 = side.add_reference_point(side_name + str(i + 2), support_zone[2][0], support_zone[2][1])
    rp18 = side.add_reference_point(side_name + str(i + 3), support_zone[3][0], support_zone[3][1])
    point_list.append([rp15, rp16, rp17, rp18])
    return point_list

def create_patrol_zone(side_name, scenario, patrol_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    rp1 = side.add_reference_point(side_name + 'xlrp' + str(i + 0), patrol_zone[0][0], patrol_zone[0][1])
    rp2 = side.add_reference_point(side_name + 'xlrp' + str(i + 1), patrol_zone[1][0], patrol_zone[1][1])
    rp3 = side.add_reference_point(side_name + 'xlrp' + str(i + 2), patrol_zone[2][0], patrol_zone[2][1])
    rp4 = side.add_reference_point(side_name + 'xlrp' + str(i + 3), patrol_zone[3][0], patrol_zone[3][1])
    point_list.append([rp1, rp2, rp3, rp4])
    return point_list
def creat_prosecution_area(side_name, scenario, prosecution_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    jj1 = side.add_reference_point(side_name + 'jjrp' + str(i + 0), prosecution_zone[0][0], prosecution_zone[0][1])
    jj2 = side.add_reference_point(side_name + 'jjrp' + str(i + 1), prosecution_zone[1][0], prosecution_zone[1][1])
    jj3 = side.add_reference_point(side_name + 'jjrp' + str(i + 2), prosecution_zone[2][0], prosecution_zone[2][1])
    jj4 = side.add_reference_point(side_name + 'jjrp' + str(i + 3), prosecution_zone[3][0], prosecution_zone[3][1])
    point_list.append([jj1, jj2, jj3, jj4])
    return point_list

def updata_mozi_order(side_name, scenario, order_dic, start_time):
    side = scenario.get_side_by_name(side_name)
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    mssnSitu = side.strikemssns
    strike_missions = [mission for mission in mssnSitu.values()]
    if order_dic.get('order_type') == ORDER_TYPE.ADD_AIR_PATROL_ORDER:
        patrol_rule = order_dic.get('order_rule')
        patrol_name = order_dic.get('order_name')
        for patrol_mission in patrol_missions:
            if patrol_mission.strName == patrol_name:
                doctrine_xl1 = patrol_mission.get_doctrine()
                doctrine_xl1.set_weapon_state_for_aircraft(patrol_rule.get('weapon_state_for_aircraft'))
                doctrine_xl1.set_weapon_state_for_air_group(patrol_rule.get('weapon_state_for_air_group'))
                doctrine_xl1.gun_strafe_for_aircraft('1')
                # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
                edit_weapon_doctrine(doctrine=doctrine_xl1, rule=patrol_rule)
    elif order_dic.get('order_type') == ORDER_TYPE.ADD_SEA_STRIKE_ORDER:
        strike_rule = order_dic.get('order_rule')
        strike_name = order_dic.get('order_name')
        # airs_dic = side.aircrafts
        # airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in [
        #     "F-16A #4"
        # ]}
        # for v in airs_strike.values():
        #     print('飞机经纬度', v.strName, v.dLatitude, v.dLongitude)
        for strike_mission in strike_missions:
            if strike_mission.strName == strike_name:
                doctrine_sk1 = strike_mission.get_doctrine()
                doctrine_sk1.set_weapon_state_for_aircraft(strike_rule.get('weapon_state_for_aircraft'))
                doctrine_sk1.set_weapon_state_for_air_group(strike_rule.get('weapon_state_for_air_group'))
                edit_anti_ship_weapon_doctrine(doctrine=doctrine_sk1, rule=strike_rule)
    elif order_dic.get('order_type') == ORDER_TYPE.UPDATE_REFENCE_POINT:
        current_simtime = scenario.get_current_time()
        if int(current_simtime) - int(start_time) >= 4000:
            old_refence_point_name_list = order_dic.get('old_support_zone_name')
            new_point_list = order_dic.get('new_support_zone')
            updata_zone(side_name, scenario, old_refence_point_name_list, new_point_list)


def edit_weapon_doctrine(doctrine, rule):
    # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384

    # AIM-120C-7
    doctrine.set_weapon_release_authority('718', '1999', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2000', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2001', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2002', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2031', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2100', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2200', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    # AIM-9M
    doctrine.set_weapon_release_authority('1384', '1999', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2000', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2001', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2002', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2021', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2031', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2100', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2200', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')

def edit_anti_ship_weapon_doctrine(doctrine, rule):
    # AGM - 84L: 816
    doctrine.set_weapon_release_authority('816', '2999', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3101', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3102', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3103', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3000', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3104', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3105', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3106', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3107', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3108', rule.get('fire_num'), rule.get('launcher'), rule.get('fire_dis'), 'none', 'false')

def updata_zone(side_name, scenario, old_refence_point_name_list, new_point_list):
    side = scenario.get_side_by_name(side_name)
    for old_name, new_point in zip(old_refence_point_name_list, new_point_list):
        side.set_reference_point(old_name, new_point[0], new_point[1])
