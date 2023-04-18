# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
# from blue_agent_lj.blue_agent_lj_comprehensive_skill.utils import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission

# lst = ['闪电 #5', '闪电 #6', '闪电 #7', '闪电 #8', '闪电 #9', '闪电 #10', '闪电 #11', '闪电 #12', '闪电 #13', '闪电 #14', '闪电 #15',
#        '闪电 #16']
# lst_1 = ['F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','EC-130H #2']
lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
# lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9', 'EC-130H #1', 'E-2K #1']
lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']

# lst_1 = ['F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9']
# lst_2 = ['EC-130H #2', 'EC-130H #1', 'E-2K #1']
lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04']
lst_4 = ['F-16A #1', 'F-16A #2','F-16A #3', 'F-16A #4']
lst_5 = ['E-2K #1']
lst_6 = ['EC-130H #1']
lst_7 = ['EC-130H #2']

# 选择不同任务的条件判断,如果红方飞机剩余小于10架，就启动反舰任务
def antiship_condition_check(side_name, scenario):
    """
    by dixit
    :param scenario:
    :param side_name
    :return:

    """
    if side_name == '蓝方':
        side_op = '红方'
    else:
        side_op = '蓝方'
    side = scenario.get_side_by_name(side_op)
    airs = side.aircrafts
    if len(airs) <= 9:
        return True
    else:
        return False


# 更新巡逻区，并创建反水面巡逻
def create_antisurfaceship_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions_2 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '2']
    # patrol_missions_3 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '3']
    # patrol_missions_4 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '4']
    strike_patrol_missions_3 = [v for v in patrol_missions_dic.values() if 'strike_patrol_3' in v.strName]

    side_red = scenario.get_side_by_name('红方')
    airs_red = side_red.aircrafts
    airs_fight_red = [v for v in airs_red.values() if '米格' in v.strName]
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}巡逻区域已更新')
    # if flag != 'Yes':
    if len(airs_fight_red) < 2:
        missionUnits_2 = patrol_missions_2[0].m_AssignedUnits.split('@')
        # missionUnits_3 = patrol_missions_3[0].m_AssignedUnits.split('@')
        # missionUnits_4 = patrol_missions_4[0].m_AssignedUnits.split('@')
        if len(strike_patrol_missions_3) == 0:
            print('开始创建反水面巡逻任务')
            point_list = create_anti_ship_zone(side_name,scenario)
            postr = []
            for point in point_list:
                for name in point:
                    postr.append(name.strName)
            strikePatrolmssn_2 = side.add_mission_patrol('strike_patrol_2', 1, postr)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strikePatrolmssn_2.set_flight_size_check('false')
            strikePatrolmssn_2.set_patrol_zone(postr)
            utils.change_unit_mission(side, patrol_missions_2[0], strikePatrolmssn_2, missionUnits_2)

            point_list_2 = create_anti_ship_zone_2(side_name, scenario)
            postr_2 = []
            for point in point_list_2:
                for name in point:
                    postr_2.append(name.strName)
            strikePatrolmssn_3 = side.add_mission_patrol('strike_patrol_3', 1, postr_2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strikePatrolmssn_3.set_flight_size_check('false')
            strikePatrolmssn_3.set_patrol_zone(postr_2)
            # utils.change_unit_mission(side, patrol_missions_3[0], strikePatrolmssn_3, missionUnits_3)


            point_list_3 = create_anti_ship_zone_3(side_name, scenario)
            postr_3 = []
            for point in point_list_3:
                for name in point:
                    postr_3.append(name.strName)
            strikePatrolmssn_4 = side.add_mission_patrol('strike_patrol_4', 1, postr_3)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strikePatrolmssn_4.set_flight_size_check('false')
            strikePatrolmssn_4.set_patrol_zone(postr_3)
            # utils.change_unit_mission(side, patrol_missions_4[0], strikePatrolmssn_4, missionUnits_4)

            ps_anti_list = create_anti_ship_prosecution_zone(side_name, scenario)
            ps_anti_list_2 = create_anti_ship_prosecution_zone_2(side_name, scenario)
            ps_anti_list_3 = create_anti_ship_prosecution_zone_3(side_name, scenario)
            ps_anti_str = []
            ps_anti_str_2 = []
            ps_anti_str_3 = []
            for ps in ps_anti_list:
                for name in ps:
                    ps_anti_str.append(name.strName)
            for ps in ps_anti_list_2:
                for name in ps:
                    ps_anti_str_2.append(name.strName)
            for ps in ps_anti_list_3:
                for name in ps:
                    ps_anti_str_3.append(name.strName)
            # strikePatrolmssn_2.set_prosecution_zone(ps_anti_str)
            # strikePatrolmssn_3.set_prosecution_zone(ps_anti_str_2)
            # strikePatrolmssn_4.set_prosecution_zone(ps_anti_str_3)

        else:
            return False
    return False

# 更新反水面巡逻任务
def update_antisurfaceship_mission(side_name, scenario):
    print('开始更新反水面巡逻任务')
    side = scenario.get_side_by_name(side_name)
    patrol_missions_dic = side.get_patrol_missions()
    strike_patrol_missions = [v for v in patrol_missions_dic.values() if v.strName in ['strike_patrol_2', 'strike_patrol_3',
                                                                                       'strike_patrol_4']]
    airs_dic = side.aircrafts
    # v is activeunit.py 中 class CActiveUnit 中的属性:
    airsOnMssn = {k: v for k, v in airs_dic.items() if v.strActiveUnitStatus.find('正在执行任务') > 0}
    # 获取在空飞机
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 9}
    airs_strike4 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_4}
    airs_strike3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_3}
    airs_strike2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_2}
    contacts = side.contacts
    # target = {k: v for k, v in contacts.items() if '航空母舰' in v.strName}
    # target = {k: v for k, v in contacts.items() if '护卫舰' in v.strName}
    target_huwei = [v for k, v in contacts.items() if '护卫舰' in v.strName]
    target_quzhu = [v for k, v in contacts.items() if '驱逐舰' in v.strName]
    # ps_anti_list = create_anti_ship_prosecution_zone(side_name, scenario)
    # ps_anti_list_2 = create_anti_ship_prosecution_zone_2(side_name, scenario)
    # ps_anti_list_3 = create_anti_ship_prosecution_zone_3(side_name, scenario)
    # ps_anti_str = []
    # ps_anti_str_2 = []
    # ps_anti_str_3 = []
    # for ps in ps_anti_list:
    #     for name in ps:
    #         ps_anti_str.append(name.strName)
    # for ps in ps_anti_list_2:
    #     for name in ps:
    #         ps_anti_str_2.append(name.strName)
    # for ps in ps_anti_list_3:
    #     for name in ps:
    #         ps_anti_str_3.append(name.strName)
    # if airsOnMssn.__len__() == 0:
    #     print('airsOnMssn')
    #     return False
    # update_anti_ship_prosection_zone(side_name, scenario)
    # update_anti_ship_prosection_zone_2(side_name, scenario)
    # update_anti_ship_prosection_zone_3(side_name, scenario)
    if len(contacts) == 0 or len(airs) == 0:
        return False
    if len(strike_patrol_missions) != 3:
        return False
    for patrol_mission in strike_patrol_missions:
        if patrol_mission.strName == 'strike_patrol_2':
            # patrol_mission.set_prosecution_zone(ps_anti_str_2)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_one_third_rule('false')
            doctrine_strxl2 = patrol_mission.get_doctrine()
            doctrine_strxl2.set_weapon_state_for_aircraft(2002)
            doctrine_strxl2.set_weapon_state_for_air_group('3')
            doctrine_strxl2.set_fuel_state_for_air_group('0')
            # AGM-84L:816
            edit_anti_ship_weapon_doctrine(doctrine=doctrine_strxl2)
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            update_anti_ship_prosection_zone(side_name, scenario)
            # for air in airs_strike2.values():
            #     doctrine = air.get_doctrine()
            #     doctrine.set_emcon_according_to_superiors('no')
            #     doctrine.set_em_control_status('Radar', 'Passive')
            # if target_huwei:
            #     geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
            #     for air in airs_strike2.values():
            #         if '返回基地' in air.strActiveUnitStatus:
            #             continue
            #         evade_ship(geopoint_target, air, doctrine_strxl2)
        if patrol_mission.strName == 'strike_patrol_3':
            # patrol_mission.set_prosecution_zone(ps_anti_str_2)
            patrol_mission.assign_units(airs_strike3)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_one_third_rule('false')
            doctrine_strxl3 = patrol_mission.get_doctrine()
            doctrine_strxl3.set_weapon_state_for_aircraft(2002)
            doctrine_strxl3.set_weapon_state_for_air_group('3')
            doctrine_strxl3.set_fuel_state_for_air_group('0')
            # AGM-84L:816
            edit_anti_ship_weapon_doctrine(doctrine=doctrine_strxl3)
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            update_anti_ship_prosection_zone_2(side_name, scenario)
            # for air in airs_strike3.values():
            #     doctrine = air.get_doctrine()
            #     doctrine.set_emcon_according_to_superiors('no')
            #     doctrine.set_em_control_status('Radar', 'Passive')
            # if target_huwei:
            #     geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
            #     for air in airs_strike3.values():
            #         if '返回基地' in air.strActiveUnitStatus:
            #             continue
            #         evade_ship(geopoint_target, air, doctrine_strxl3)
        if patrol_mission.strName == 'strike_patrol_4':
            # patrol_mission.set_prosecution_zone(ps_anti_str_3)
            patrol_mission.set_one_third_rule('false')
            doctrine_strxl4 = patrol_mission.get_doctrine()
            doctrine_strxl4.set_weapon_state_for_aircraft(2002)
            doctrine_strxl4.set_weapon_state_for_air_group('3')
            doctrine_strxl4.set_fuel_state_for_air_group('0')
            # AGM-84L:816
            edit_anti_ship_weapon_doctrine(doctrine=doctrine_strxl4)
            patrol_mission.assign_units(airs_strike4)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            update_anti_ship_prosection_zone_3(side_name, scenario)
            # for air in airs_strike4.values():
            #     doctrine = air.get_doctrine()
            #     doctrine.set_emcon_according_to_superiors('no')
            #     doctrine.set_em_control_status('Radar', 'Passive')
            # if target_huwei:
            #     geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
            #     for air in airs_strike4.values():
            #         if '返回基地' in air.strActiveUnitStatus:
            #             continue
            #         evade_ship(geopoint_target, air, doctrine_strxl4)
    # if '沉没' in target[0].strActiveUnitStatus:
    #     update_anti_ship_zone(side_name, scenario)
    return False


# 更新巡逻任务
def update_patrol_mission(side_name, scenario):
    print('开始更新巡逻任务')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    air_target_red = side.contacts
    target_mige = [v for k, v in air_target_red.items() if '米格' in v.strName]
    # airs_in_sky = [v for v in target_mige if '在空' in v.strActiveUnitStatus]
    # 获取巡逻任务，如果巡逻任务为0，说明还没有，创建巡逻任务。
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    if len(patrol_missions) == 0:
        return False

    point_prosecution_list = creat_prosecution_area(side_name, scenario)
    point_prosecution_list_2 = creat_prosecution_area_2(side_name, scenario)
    # point_prosecution_list_3 = creat_prosecution_area_3(side_name, scenario)
    # point_prosecution_list_4 = creat_prosecution_area_4(side_name, scenario)
    ps_str = []
    ps_str_2 = []
    ps_str_3 = []
    ps_str_4 = []
    for ps in point_prosecution_list:
        for name in ps:
            ps_str.append(name.strName)
    for ps in point_prosecution_list_2:
        for name in ps:
            ps_str_2.append(name.strName)
    # for ps in point_prosecution_list_3:
    #     for name in ps:
    #         ps_str_3.append(name.strName)
    # for ps in point_prosecution_list_4:
    #     for name in ps:
    #         ps_str_4.append(name.strName)
    # 如果有任务，就每个任务更新，包含给任务分配飞机，1/3规则
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + 'xl1':
            patrol_mission.set_prosecution_zone(ps_str)
            doctrine_xl1 = patrol_mission.get_doctrine()
            doctrine_xl1.set_weapon_state_for_aircraft(2002)
            doctrine_xl1.set_weapon_state_for_air_group('3')
            doctrine_xl1.gun_strafe_for_aircraft('1')
            # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
            edit_weapon_doctrine(doctrine=doctrine_xl1)
            airs_xl1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_1}
            patrol_mission.assign_units(airs_xl1)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            # patrol_mission.set_throttle_transit('Cruise')
            edit_thort_doctrine(patrol_mission)

            # for air in airs_xl1.values():
            #     doctrine = air.get_doctrine()
            #     doctrine.set_emcon_according_to_superiors('no')
            #     doctrine.set_em_control_status('Radar', 'Passive')

        elif patrol_mission.strName == side_name + 'xl2':
            patrol_mission.set_prosecution_zone(ps_str_2)
            doctrine_xl2 = patrol_mission.get_doctrine()
            doctrine_xl2.set_weapon_state_for_aircraft(2002)
            doctrine_xl2.set_weapon_state_for_air_group('3')
            doctrine_xl2.gun_strafe_for_aircraft('1')
            # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
            edit_weapon_doctrine(doctrine=doctrine_xl2)
            airs_xl2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_2}
            patrol_mission.assign_units(airs_xl2)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            # patrol_mission.set_throttle_transit('Cruise')
            edit_thort_doctrine(patrol_mission)
            # for air in airs_xl2.values():
            #     doctrine = air.get_doctrine()
            #     doctrine.set_emcon_according_to_superiors('no')
            #     doctrine.set_em_control_status('Radar', 'Passive')

    # 更新支援任务，设置条令
    support_missions_dic = side.get_support_missions()
    support_missions_1 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '1']
    airs_support1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_5}
    airs_support2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_6}
    airs_support3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_7}
    if len(support_missions_1) != 0:
        for air in airs_support1.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('Radar', 'Active')
    support_missions_2 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '2']
    if len(support_missions_2) != 0:
        for air in airs_support2.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
    support_missions_3 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '3']
    if len(support_missions_3) != 0:
        for air in airs_support3.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
    return False


# 躲避护卫舰接口
def evade_ship(geopoint_target, air, mission_doctrine):
    geopoint_air = (air.dLatitude, air.dLongitude)
    if geopoint_target:
        dis = get_horizontal_distance(geopoint_air, geopoint_target)
        if dis <= 80:
            mission_doctrine.ignore_plotted_course('yes')
            # genpoint_away = get_end_point(geopoint_air, 15, (air.fCurrentHeading + 150))
            genpoint_away = (geopoint_target[0] + 0.13, geopoint_target[1] - 0.3)
            # genpoint_away_1 = (geopoint_target[0] - 0.18, geopoint_target[1] - 0.1)
            # genpoint_away_2 = (geopoint_target[0] + 0.18, geopoint_target[1] + 0.18)
            air.plot_course([genpoint_away])
            edit_anti_ship_weapon_doctrine(mission_doctrine)


# 躲避驱逐舰接口
def evade_ship_1(geopoint_target, air, mission_doctrine):
    geopoint_air = (air.dLatitude, air.dLongitude)
    if geopoint_target:
        dis = get_horizontal_distance(geopoint_air, geopoint_target)
        print('dis=',dis)
        if dis <= 100:
            mission_doctrine.ignore_plotted_course('yes')
            # genpoint_away = get_end_point(geopoint_air, 15, (air.fCurrentHeading + 150))
            # latitude = '18.878892602869', longitude = '124.65764519914'
            # latitude = '18.979253128597', longitude = '124.474929323515'
            genpoint_away = (geopoint_target[0] + 0.1, geopoint_target[1] - 0.2)
            air.plot_course([genpoint_away])
            edit_anti_ship_weapon_doctrine(mission_doctrine)

# 创建巡逻任务
def create_patrol_mission(side_name, scenario):
    print('开始创建巡逻任务')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs_support1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_5}
    airs_support2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_6}
    airs_support3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_7}
    patrol_missions_dic = side.get_patrol_missions()
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}巡逻任务已创建')
    if flag == 'Yes':
        return False
    # patrol_missions_dic = side.get_patrol_missions()
    patrol_mission_name = [mission.strName for mission in patrol_missions_dic.values()]

    point_list = create_patrol_zone(side_name, scenario)
    # 创建2个巡逻区，一起行动
    i = 1
    for point in point_list:
        point_str = []
        for name in point:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + 'xl' + str(i)

        # 创建巡逻任务，设置1/3规则
        patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str)
        print('巡逻任务已创建')
        patrolmssn.set_one_third_rule('false')
        patrolmssn.set_patrol_zone(point_str)
        i += 1
    # 建立支援任务1
    support_point_list = support_zone_for_two(side_name, scenario)
    for point in support_point_list:
        point_str_support = []
        for name in point:
            point_str_support.append(name.strName)
        support_name = side_name + 'support' + str(1)
        supportmssn = side.add_mission_support(support_name, point_str_support)
        print('支援任务1已创建')
        supportmssn.set_is_active('true')
        supportmssn.assign_units(airs_support1)
        supportmssn.set_one_third_rule('false')
        supportmssn.set_flight_size(1)
        supportmssn.set_flight_size_check('false')
    # # 建立支援任务2
    for point in support_point_list:
        point_str_support = []
        for name in point:
            point_str_support.append(name.strName)
        support_name = side_name + 'support' + str(2)
        supportmssn = side.add_mission_support(support_name, point_str_support)
        print('支援任务2已创建')
        supportmssn.set_is_active('true')
        supportmssn.assign_units(airs_support2)
        supportmssn.set_one_third_rule('false')
        supportmssn.set_flight_size(1)
        supportmssn.set_flight_size_check('false')
    # # 建立支援任务3
    support_point_list_2 = support_zone_for_one(side_name, scenario)
    for point in support_point_list_2:
        point_str_support = []
        for name in point:
            point_str_support.append(name.strName)
        support_name = side_name + 'support' + str(3)
        supportmssn = side.add_mission_support(support_name, point_str_support)
        print('支援任务3已创建')
        supportmssn.set_is_active('true')
        supportmssn.assign_units(airs_support3)
        supportmssn.set_one_third_rule('false')
        supportmssn.set_flight_size(1)
        supportmssn.set_flight_size_check('false')

    scenario.mozi_server.set_key_value(f'{side_name}巡逻任务已创建', 'Yes')
    return False

# 巡逻区域经纬度的生成
def create_patrol_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(21.8210656716398, 122.356667127581), (21.8752434450009, 122.768058783733),
               (21.6698815188537, 122.741326377829), (21.6701551543473, 122.35337044599)]
    # latitude = '21.3051162778855', longitude = '122.379458695445'
    # latitude = '21.2990241499901', longitude = '122.655496064203'
    # latitude = '21.1422240635319', longitude = '122.62857581968'
    # latitude = '21.1107003504574', longitude = '122.399977138059'
    # point_1 = [(21.3051162778855, 122.379458695445), (21.2990241499901, 122.655496064203),
    #            (21.1422240635319, 122.62857581968), (21.1107003504574, 122.399977138059)]
    # latitude = '20.8320681881964', longitude = '122.572136578965'
    # latitude = '20.8446923641533', longitude = '122.773884516692'
    # latitude = '20.6563445221476', longitude = '122.781532943064'
    # latitude = '20.6618224714281', longitude = '122.566587999268'
    # point_1 = [(20.8320681881964, 122.572136578965), (20.8446923641533, 122.773884516692),
    #            (20.6563445221476, 122.781532943064), (20.6618224714281, 122.566587999268)]
    # point_1 = [(20.8612760556798, 122.97096027272), (20.89954721661, 123.18875736993),
    #            (20.7431007450093, 123.145339607124), (20.7359032286196, 122.92736887149)]
    # lat: 纬度， lon：经度
    # xl1
    rp1 = side.add_reference_point(side_name + 'rp1', point_1[0][0], point_1[0][1])
    rp2 = side.add_reference_point(side_name + 'rp2', point_1[1][0], point_1[1][1])
    rp3 = side.add_reference_point(side_name + 'rp3', point_1[2][0], point_1[2][1])
    rp4 = side.add_reference_point(side_name + 'rp4', point_1[3][0], point_1[3][1])
    point_list.append([rp1, rp2, rp3, rp4])

    rp9 = side.add_reference_point(side_name + 'rp9', point_1[0][0], point_1[0][1])
    rp10 = side.add_reference_point(side_name + 'rp10', point_1[1][0], point_1[1][1])
    rp11 = side.add_reference_point(side_name + 'rp11', point_1[2][0], point_1[2][1])
    rp12 = side.add_reference_point(side_name + 'rp12', point_1[3][0], point_1[3][1])
    point_list.append([rp9, rp10, rp11, rp12])

    # rp24 = side.add_reference_point(side_name + 'rp24', point_1[0][0], point_1[0][1])
    # rp25 = side.add_reference_point(side_name + 'rp25', point_1[1][0], point_1[1][1])
    # rp26 = side.add_reference_point(side_name + 'rp26', point_1[2][0], point_1[2][1])
    # rp27 = side.add_reference_point(side_name + 'rp27', point_1[3][0], point_1[3][1])
    # point_list.append([rp24, rp25, rp26, rp27])
    #
    # rp28 = side.add_reference_point(side_name + 'rp28', point_1[0][0], point_1[0][1])
    # rp29 = side.add_reference_point(side_name + 'rp29', point_1[1][0], point_1[1][1])
    # rp30 = side.add_reference_point(side_name + 'rp30', point_1[2][0], point_1[2][1])
    # rp31 = side.add_reference_point(side_name + 'rp31', point_1[3][0], point_1[3][1])
    # point_list.append([rp28, rp29, rp30, rp31])
    return point_list

# 设置警戒区的区域1
def creat_prosecution_area(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981),
               (21.705618145078,123.70585754102), (21.2291643151066,121.162975576448)]
    rp5 = side.add_reference_point(side_name + 'rp5', point_1[0][0], point_1[0][1])
    rp6 = side.add_reference_point(side_name + 'rp6', point_1[1][0], point_1[1][1])
    rp7 = side.add_reference_point(side_name + 'rp7', point_1[2][0], point_1[2][1])
    rp8 = side.add_reference_point(side_name + 'rp8', point_1[3][0], point_1[3][1])
    point_list.append([rp5, rp6, rp7, rp8])
    return point_list

# 设置警戒区的区域2
def creat_prosecution_area_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981),
               (21.705618145078,123.70585754102), (21.2291643151066,121.162975576448)]
    rp32 = side.add_reference_point(side_name + 'rp32', point_1[0][0], point_1[0][1])
    rp33 = side.add_reference_point(side_name + 'rp33', point_1[1][0], point_1[1][1])
    rp34 = side.add_reference_point(side_name + 'rp34', point_1[2][0], point_1[2][1])
    rp35 = side.add_reference_point(side_name + 'rp35', point_1[3][0], point_1[3][1])
    point_list.append([rp32, rp33, rp34, rp35])
    return point_list
# 设置警戒区的区域3
def creat_prosecution_area_3(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981),
               (21.705618145078,123.70585754102), (21.2291643151066,121.162975576448)]
    rp36 = side.add_reference_point(side_name + 'rp36', point_1[0][0], point_1[0][1])
    rp37 = side.add_reference_point(side_name + 'rp37', point_1[1][0], point_1[1][1])
    rp38 = side.add_reference_point(side_name + 'rp38', point_1[2][0], point_1[2][1])
    rp39 = side.add_reference_point(side_name + 'rp39', point_1[3][0], point_1[3][1])
    point_list.append([rp36, rp37, rp38, rp39])
    return point_list

# 设置警戒区的区域4
def creat_prosecution_area_4(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981),
               (21.705618145078,123.70585754102), (21.2291643151066,121.162975576448)]
    rp40 = side.add_reference_point(side_name + 'rp40', point_1[0][0], point_1[0][1])
    rp41 = side.add_reference_point(side_name + 'rp41', point_1[1][0], point_1[1][1])
    rp42 = side.add_reference_point(side_name + 'rp42', point_1[2][0], point_1[2][1])
    rp43 = side.add_reference_point(side_name + 'rp43', point_1[3][0], point_1[3][1])
    point_list.append([rp40, rp41, rp42, rp43])
    return point_list
# 用于巡逻任务中编辑武器条令,空空弹武器条例
def edit_weapon_doctrine(doctrine):
    # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384

    # AIM-120C-7
    doctrine.set_weapon_release_authority('718', '1999', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2000', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2001', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2002', '2', '1', '80', 'none', 'false')
    # doctrine.set_weapon_release_authority('718', '2021', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2031', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2100', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('718', '2200', '2', '1', '80', 'none', 'false')
    # AIM-9M
    doctrine.set_weapon_release_authority('1384', '1999', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2000', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2001', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2002', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2021', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2031', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2100', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('1384', '2200', '2', '1', '80', 'none', 'false')

# 用于打击任务中编辑武器条令,反舰弹武器条例
def edit_anti_ship_weapon_doctrine(doctrine):
    # AGM - 84L: 816
    doctrine.set_weapon_release_authority('816', '2999', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3101', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3102', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3103', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3000', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3104', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3105', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3106', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3107', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('816', '3108', '2', '1', '80', 'none', 'false')
# 设置巡逻任务的油门、巡航的条例
def edit_thort_doctrine(patrol_mission):
    patrol_mission.set_throttle_transit('Loiter')
    patrol_mission.set_throttle_station('Loiter')
    patrol_mission.set_throttle_attack('Loiter')
    # patrol_mission.set_transit_altitude(13000.0)
    # patrol_mission.set_station_altitude(13000.0)
# 第一次更新巡逻区1
def update_patrol_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798,122.97096027272),(20.89954721661,123.18875736993),
               (20.7431007450093,123.145339607124), (20.7359032286196,122.92736887149)]
    side.set_reference_point(side_name + 'rp1', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp2', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp3', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp4', point_2[3][0], point_2[3][1])

# 第一次更新巡逻区2
def update_patrol_zone_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798,122.97096027272),(20.89954721661,123.18875736993),
               (20.7431007450093,123.145339607124), (20.7359032286196,122.92736887149)]
    side.set_reference_point(side_name + 'rp9', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp10', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp11', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp12', point_2[3][0], point_2[3][1])
# 第一次更新巡逻区3
def update_patrol_zone_3(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798,122.97096027272),(20.89954721661,123.18875736993),
               (20.7431007450093,123.145339607124), (20.7359032286196,122.92736887149)]
    side.set_reference_point(side_name + 'rp24', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp25', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp26', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp27', point_2[3][0], point_2[3][1])
# 第一次更新巡逻区4
def update_patrol_zone_4(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798,122.97096027272),(20.89954721661,123.18875736993),
               (20.7431007450093,123.145339607124), (20.7359032286196,122.92736887149)]
    side.set_reference_point(side_name + 'rp28', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp29', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp30', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp31', point_2[3][0], point_2[3][1])
# 第二次更新巡逻区1
def update_patrol_zone_1_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.2144470484764, 123.516169865535), (20.2278627578651, 123.649988700678),
               (20.0659610132846, 123.646671081285), (20.0921963717958, 123.523460225537)]
    # latitude = '17.9470604068874', longitude = '124.103556417016'
    # latitude = '17.9876589367439', longitude = '124.292705295125'
    # latitude = '17.7895390322961', longitude = '124.292598174033'
    # latitude = '17.7955410590435', longitude = '124.079160952229'
    # hwj latitude='17.8808636810558', longitude='124.811513939545'
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp1', lat1+0.1, lon1-0.7)
            side.set_reference_point(side_name + 'rp2', lat1+0.1, lon1-0.6)
            side.set_reference_point(side_name + 'rp3', lat1-0.1, lon1-0.6)
            side.set_reference_point(side_name + 'rp4', lat1-0.1, lon1-0.7)
# 第二次更新巡逻区2
def update_patrol_zone_2_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.2144470484764, 123.516169865535), (20.2278627578651, 123.649988700678),
               (20.0659610132846, 123.646671081285), (20.0921963717958, 123.523460225537)]
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp9', lat1+0.1, lon1-0.7)
            side.set_reference_point(side_name + 'rp10', lat1+0.1, lon1-0.6)
            side.set_reference_point(side_name + 'rp11', lat1-0.1, lon1-0.6)
            side.set_reference_point(side_name + 'rp12', lat1-0.1, lon1-0.7)
# 第二次更新巡逻区3
def update_patrol_zone_3_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.2144470484764, 123.516169865535), (20.2278627578651, 123.649988700678),
               (20.0659610132846, 123.646671081285), (20.0921963717958, 123.523460225537)]
    side.set_reference_point(side_name + 'rp24', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp25', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp26', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp27', point_2[3][0], point_2[3][1])
# 第二次更新巡逻区4
def update_patrol_zone_4_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.2144470484764, 123.516169865535), (20.2278627578651, 123.649988700678),
               (20.0659610132846, 123.646671081285), (20.0921963717958, 123.523460225537)]
    side.set_reference_point(side_name + 'rp28', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp29', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp30', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp31', point_2[3][0], point_2[3][1])
# 更新预警机支援的区域
def update_support_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798, 122.97096027272), (20.89954721661, 123.18875736993),
               (20.7431007450093, 123.145339607124), (20.7359032286196, 122.92736887149)]
    side.set_reference_point(side_name + 'rp15', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp16', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp17', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp18', point_2[3][0], point_2[3][1])
# 给3个对海打击任务设置油门，试试效果
def edit_attack_throttle_for_strike(strike_mission):
    strike_mission.set_throttle('attackThrottleAircraft', 'Flank')
    # 老版的接口有，现在没有了
    # strike_mission.set_speed('attackSpeedAircraft',1700.0)
# 新增预警机和干扰机支援任务的区域
def support_zone_for_two(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(21.8764427622847, 121.330904108449), (21.8335734773605, 121.478618597081),
               (21.6920926322308, 121.580152213845), (21.6899037180596, 121.405076571889)]
    rp15 = side.add_reference_point(side_name + 'rp15', point_1[0][0], point_1[0][1])
    rp16 = side.add_reference_point(side_name + 'rp16', point_1[1][0], point_1[1][1])
    rp17 = side.add_reference_point(side_name + 'rp17', point_1[2][0], point_1[2][1])
    rp18 = side.add_reference_point(side_name + 'rp18', point_1[3][0], point_1[3][1])
    point_list.append([rp15, rp16, rp17, rp18])
    return point_list

# 新增干扰机支援任务的区域
def support_zone_for_one(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(22.4098475117646, 122.186072181501), (22.418764139488, 122.367143273071),
               (22.233752742808, 122.386191481229), (22.2336414046035, 122.186317353378)]
    rp20 = side.add_reference_point(side_name + 'rp20', point_1[0][0], point_1[0][1])
    rp21 = side.add_reference_point(side_name + 'rp21', point_1[1][0], point_1[1][1])
    rp22 = side.add_reference_point(side_name + 'rp22', point_1[2][0], point_1[2][1])
    rp23 = side.add_reference_point(side_name + 'rp23', point_1[3][0], point_1[3][1])
    point_list.append([rp20, rp21, rp22, rp23])
    return point_list
# 创建反水面巡逻区
def create_anti_ship_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    # hw latitude = '19.2065652756537', longitude = '125.331704335909'
    # latitude = '19.223322738813', longitude = '125.29481225696'
    # latitude = '19.2306730249893', longitude = '125.366652637037'
    # latitude = '19.1665097331383', longitude = '125.384127475361'
    # latitude = '19.1646490983331', longitude = '125.283199433689'
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp44 = side.add_reference_point(side_name + 'rp44', lat1+0.02, lon1-0.03)
            rp45 = side.add_reference_point(side_name + 'rp45', lat1+0.03, lon1+0.03)
            rp46 = side.add_reference_point(side_name + 'rp46', lat1-0.04, lon1+0.05)
            rp47 = side.add_reference_point(side_name + 'rp47', lat1-0.04, lon1-0.05)
            point_list.append([rp44, rp45, rp46, rp47])
    return point_list

# 创建反水面巡逻区2
def create_anti_ship_zone_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp48 = side.add_reference_point(side_name + 'rp48', lat1+0.02, lon1-0.03)
            rp49 = side.add_reference_point(side_name + 'rp49', lat1+0.03, lon1+0.03)
            rp50 = side.add_reference_point(side_name + 'rp50', lat1-0.04, lon1+0.05)
            rp51 = side.add_reference_point(side_name + 'rp51', lat1-0.04, lon1-0.05)
            point_list.append([rp48, rp49, rp50, rp51])
    return point_list

# 创建反水面巡逻区3
def create_anti_ship_zone_3(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp52 = side.add_reference_point(side_name + 'rp52', lat1+0.02, lon1-0.03)
            rp53 = side.add_reference_point(side_name + 'rp53', lat1+0.03, lon1+0.03)
            rp54 = side.add_reference_point(side_name + 'rp54', lat1-0.04, lon1+0.05)
            rp55 = side.add_reference_point(side_name + 'rp55', lat1-0.04, lon1-0.05)
            point_list.append([rp52, rp53, rp54, rp55])
    return point_list
# 更新反水面巡逻区
def update_anti_ship_zone(side_name, scenario):# 没有用
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    # 根据对方驱逐舰位置创建巡逻区 xl4
    for contact in contacts.values():
        if '驱逐舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp44', lat1 + 0.26, lon1 - 0.6)
            side.set_reference_point(side_name + 'rp45', lat1 + 0.26, lon1 - 0.4)
            side.set_reference_point(side_name + 'rp46', lat1 + 0.1, lon1 - 0.5)
            side.set_reference_point(side_name + 'rp47', lat1 + 0.09, lon1 - 0.6)

# 创建反水面警戒区
def create_anti_ship_prosecution_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp56 = side.add_reference_point(side_name + 'rp56', lat1 + 0.03, lon1 - 0.2)
            rp57 = side.add_reference_point(side_name + 'rp57', lat1 + 0.04, lon1 - 0.18)
            rp58 = side.add_reference_point(side_name + 'rp58', lat1 - 0.01, lon1 - 0.16)
            rp59 = side.add_reference_point(side_name + 'rp59', lat1 - 0.01, lon1 - 0.22)
            point_list.append([rp56, rp57, rp58, rp59])
    return point_list
# 创建反水面警戒区2
def create_anti_ship_prosecution_zone_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp60 = side.add_reference_point(side_name + 'rp60', lat1 + 0.03, lon1 - 0.2)
            rp61 = side.add_reference_point(side_name + 'rp61', lat1 + 0.04, lon1 - 0.18)
            rp62 = side.add_reference_point(side_name + 'rp62', lat1 - 0.01, lon1 - 0.16)
            rp63 = side.add_reference_point(side_name + 'rp63', lat1 - 0.01, lon1 - 0.22)
            point_list.append([rp60, rp61, rp62, rp63])
    return point_list

# 创建反水面警戒区3
def create_anti_ship_prosecution_zone_3(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    contacts = side.contacts
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            rp64 = side.add_reference_point(side_name + 'rp64', lat1 + 0.03, lon1 - 0.2)
            rp65 = side.add_reference_point(side_name + 'rp65', lat1 + 0.04, lon1 - 0.18)
            rp66 = side.add_reference_point(side_name + 'rp66', lat1 - 0.01, lon1 - 0.16)
            rp67 = side.add_reference_point(side_name + 'rp67', lat1 - 0.01, lon1 - 0.22)
            point_list.append([rp64, rp65, rp66, rp67])
    return point_list

# 更新反水面巡逻区
def update_anti_ship_prosection_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    # hwl latitude = '19.2030297254933', longitude = '125.333489977418'
    # latitude = '19.2708294867602', longitude = '125.247962756863'
    # latitude = '19.2690635679181', longitude = '125.453868277245'
    # latitude = '19.1022206369419', longitude = '125.430561671222'
    # latitude = '19.1186220271273', longitude = '125.240390660029'
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp44', lat1 + 0.07, lon1 - 0.09)
            side.set_reference_point(side_name + 'rp45', lat1 + 0.06, lon1 + 0.12)
            side.set_reference_point(side_name + 'rp46', lat1 - 0.1, lon1 + 0.1)
            side.set_reference_point(side_name + 'rp47', lat1 - 0.09, lon1 - 0.09)


# 更新反水面xl区2
def update_anti_ship_prosection_zone_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    # 根据对方驱逐舰位置创建巡逻区 xl4
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp48', lat1 + 0.07, lon1 - 0.09)
            side.set_reference_point(side_name + 'rp49', lat1 + 0.06, lon1 + 0.12)
            side.set_reference_point(side_name + 'rp50', lat1 - 0.1, lon1 + 0.1)
            side.set_reference_point(side_name + 'rp51', lat1 - 0.09, lon1 - 0.09)

# 更新反水面警xl3
def update_anti_ship_prosection_zone_3(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    # 根据对方驱逐舰位置创建巡逻区 xl4
    for contact in contacts.values():
        if '护卫舰' in contact.strName:
            lat1, lon1 = contact.dLatitude, contact.dLongitude
            side.set_reference_point(side_name + 'rp52', lat1 + 0.07, lon1 - 0.09)
            side.set_reference_point(side_name + 'rp53', lat1 + 0.06, lon1 + 0.12)
            side.set_reference_point(side_name + 'rp54', lat1 - 0.1, lon1 + 0.1)
            side.set_reference_point(side_name + 'rp55', lat1 - 0.09, lon1 - 0.09)
