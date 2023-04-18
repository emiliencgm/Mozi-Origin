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
    if len(airs) <= 13:
        return True
    else:
        return False


# 创建反舰任务,这个版本试试效果，把两个巡逻任务分开执行，放到打击任务前执行，如果红方飞机少于10架就执行打击任务，巡逻任务每次出动5架战机，看看能不能最大限度消灭敌方战机并保存自己
def create_antisurfaceship_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions_2 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '2']
    if len(patrol_missions_2) == 0:
        xl1_lat = 0
        xl1_lon = 0
        xl2_lat = 0
        xl2_lon = 0
        # for point in side.referencepnts.values():
        #     if point.strName == 'RP-3678':
        #         xl2_lat = point.dLatitude
        #         xl2_lon = point.dLongitude

        point_list_1 = create_patrol_zone_1(side_name, scenario)
        for point in point_list_1:
            postr = []
            for name in point:
                postr.append(name.strName)
            patrol_name = side_name + 'xl' + '2'
            Patrolmssn2 = side.add_mission_patrol(patrol_name, 0, postr)
            Patrolmssn2.set_one_third_rule('false')
            Patrolmssn2.set_patrol_zone(postr)
            airs_xl2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_2}
            Patrolmssn2.assign_units(airs_xl2)
            Patrolmssn2.set_flight_size(1)
            Patrolmssn2.set_flight_size_check('false')
            Patrolmssn2.set_opa_check('true')
            Patrolmssn2.set_wwr_check('true')
            Patrolmssn2.set_emcon_usage('false')
            # for air in airs_xl2.values():
            #     if air:
            #         # print('air2', air.strName)
            #         # air.get_valid_weapon_load()
            #         if '返回基地' in air.strActiveUnitStatus:
            #             continue
            #         # 航路点设置
            #         # air.plot_course([(xl2_lat, xl2_lon)])
            #         if air.strName == 'EC-130H #1':
            #             doctrine = air.get_doctrine()
            #             doctrine.set_em_control_status('OECM', 'Active')
            #             # air.plot_course([(xl2_lat + 1, xl2_lon - 0.2)])
            #         if air.strName == 'E-2K #1':
            #             doctrine = air.get_doctrine()
            #             doctrine.set_em_control_status('Radar', 'Active')
            #             # air.plot_course([(xl2_lat + 1, xl2_lon - 0.2)])

    side_red = scenario.get_side_by_name('红方')
    airs_red = side_red.aircrafts
    airs_fight_red = [v for v in airs_red.values() if '米格' in v.strName]
    if len(airs_fight_red) <= 2:
        print('开始创建反舰任务')
        # 获取要打击的水面舰艇单元
        contacts = side.contacts

        # 获取反舰任务飞机
        # F16A#1 #2
        airs_1 = {k: v for k, v in airs_dic.items() if v.strName in lst_3}
        # F16A#3 #4
        airs_2 = {k: v for k, v in airs_dic.items() if v.strName in lst_4}
        if len(contacts) == 0 or len(airs_1) + len(airs_2) == 0:
            return False
        # 等巡逻的飞机全部起飞后，打击任务创建，然后开始起飞
        airs_patrol = side.patrolmssns
        if not airs_patrol:
            return False
        target_list = [v.strName for v in contacts.values()]
        targets = {k: v for k, v in contacts.items() if (('航空母舰' in v.strName) | ('护卫舰' in v.strName) | ('驱逐舰' in v.strName))}
        target_1 = {k: v for k, v in contacts.items() if ('护卫舰' in v.strName)}
        # target_1 = {k: v for k, v in contacts.items() if ('航空母舰' in v.strName)}
        target_2 = {k: v for k, v in contacts.items() if ('驱逐舰' in v.strName)}
        for k, v in targets.items():
            # set_mark_contact设置目标对抗关系,H is 敌方
            side.set_mark_contact(k, 'U')
        mssnSitu = side.strikemssns
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
            strkmssn_1 = side.add_mission_strike('strike1', 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_1.set_flight_size(1)
            strkmssn_1.set_flight_size_check('false')
        else:
            return False
        # 根据敌方护卫舰的位置创建打击行动航线，试试效果
        ship_cor_point_list = []
        for k, v in target_1.items():
            strkmssn_1.assign_unit_as_target(k)

        for k, v in target_1.items():
            # strkmssn_1.assign_unit_as_target(k)
            ship_cor_point_list.append(v.dLatitude)
            ship_cor_point_list.append(v.dLongitude)
        strkmssn_1.assign_units(airs_1)
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike2'}.__len__() == 0:
            strkmssn_2 = side.add_mission_strike('strike2', 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_2.set_flight_size(1)
            strkmssn_2.set_flight_size_check('false')
        else:
            return False
        for k, v in target_1.items():
            strkmssn_2.assign_unit_as_target(k)
        strkmssn_2.assign_units(airs_2)
        # 通过 ctrl +x 拿到航线设置的点
        # side.add_plan_way(0, 'strike1Way')
        # side.add_plan_way(0, 'strike2Way')
        side.add_plan_way(0, '航线2')
        # 增加两个返航航线,strike5Way,strike6Way
        side.add_plan_way(0, 'strike5Way')
        side.add_plan_way(0, 'strike6Way')
        wayPointList1 = [{'latitude': 20.2139177649022, 'longitude': 123.50045418725},
                         {'latitude': 19.5518664351576, 'longitude': 124.05643194928},
                         {'latitude': 18.5488841549312, 'longitude': 124.272883564926}]
        cor_temp = [18.5488841549312, 124.272883564926]
        # latitude = '18.6552517376526', longitude = '124.169534717611'
        # latitude = '18.7708563446471', longitude = '124.39855499085'
        dis_ship_cor = get_horizontal_distance(ship_cor_point_list, cor_temp)
        if dis_ship_cor > 30:
            wayPointList1[2]['latitude'] += 0.0
            wayPointList1[2]['longitude'] += 0.0
        # latitude = '20.2139177649022', longitude = '123.50045418725'
        # latitude = '19.5518664351576', longitude = '124.05643194928'
        # latitude = '18.935903468962', longitude = '124.386893964303'
        # 试试这组点
        wayPointList2 = [{'latitude': 20.0757866251387, 'longitude': 124.348583728704},
                         {'latitude': 19.8203833788561, 'longitude': 124.844006741679},
                         {'latitude': 19.3408129429909, 'longitude': 125.055033853143}]
        # for item in wayPointList2:
        #     side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        # if len(way_point_list_1) != 0:
        #     for item in way_point_list_1:
        #         side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        # else:
        #     for item in wayPointList2:
        #         side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        # for item in wayPointList1:
        #     side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        strkmssn_1.add_plan_way_to_mission(0, '航线2')

        # for item in wayPointList1:
        #     side.add_plan_way_point('strike2Way', item['longitude'], item['latitude'])
        strkmssn_2.add_plan_way_to_mission(0, '航线2')
        return_way_point_list = [{'latitude': 18.3510495968947, 'longitude': 122.572064304083},
                         {'latitude': 19.0489496320236, 'longitude': 121.738389332461},
                         {'latitude': 19.989922654655, 'longitude': 121.340781278916}]
        # 试试这组返航航线
        # latitude = '19.1561939434247', longitude = '123.841144249493'
        # latitude = '19.6332044658959', longitude = '123.3016667523'
        # latitude = '20.3441967218996', longitude = '122.835832334586'
        return_way_point_list = [{'latitude': 19.1561939434247, 'longitude': 123.841144249493},
                                 {'latitude': 19.6332044658959, 'longitude': 123.3016667523},
                                 {'latitude': 20.3441967218996, 'longitude': 122.835832334586}]
        for item in return_way_point_list:
            side.add_plan_way_point('strike5Way', item['longitude'], item['latitude'])
        strkmssn_1.add_plan_way_to_mission(2, 'strike5Way')
        for item in return_way_point_list:
            side.add_plan_way_point('strike6Way', item['longitude'], item['latitude'])
        strkmssn_2.add_plan_way_to_mission(2, 'strike6Way')
        return False
    else:
        return False

# 更新反舰打击任务
def update_antisurfaceship_mission(side_name, scenario):
    print('开始更新反舰任务和巡逻2任务')
    side = scenario.get_side_by_name(side_name)
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions_2 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '2']
    if len(patrol_missions_2) != 0:
        point_prosecution_list = creat_prosecution_area(side_name, scenario)
        ps_str = []
        for ps in point_prosecution_list:
            for name in ps:
                ps_str.append(name.strName)
        for patrol_mission in patrol_missions_2:
            if patrol_mission.strName == side_name + 'xl2':
                patrol_mission.set_prosecution_zone(ps_str)
                # edit_thort_doctrine(patrol_mission)
                # doctrine_xl2 = patrol_mission.get_doctrine()
                # edit_weapon_doctrine(doctrine=doctrine_xl2)

    airs_dic = side.aircrafts
    # v is activeunit.py 中 class CActiveUnit 中的属性:
    airsOnMssn = {k: v for k, v in airs_dic.items() if v.strActiveUnitStatus.find('正在执行任务') > 0}
    # 获取在空飞机
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 9}
    contacts = side.contacts
    # target = {k: v for k, v in contacts.items() if '航空母舰' in v.strName}
    target = {k: v for k, v in contacts.items() if '护卫舰' in v.strName}
    target_strike3 = {k: v for k, v in contacts.items() if '驱逐舰' in v.strName}
    # if airsOnMssn.__len__() == 0:
    #     print('airsOnMssn')
    #     return False
    if len(contacts) == 0 or len(airs) == 0:
        return False

    mssnSitu = side.strikemssns
    strkmssn = [v for v in mssnSitu.values() if 'strike' in v.strName]
    if len(strkmssn) != 2:
        airs_strike2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_4}
        airs_strike1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_3}
        airs_strike3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_2}
        target_huwei = [v for k, v in contacts.items() if '护卫舰' in v.strName]
        target_quzhu = [v for k, v in contacts.items() if '驱逐舰' in v.strName]
        strike2_temp = [v for v in mssnSitu.values() if v.strName == 'strike2']
        strike1_temp = [v for v in mssnSitu.values() if v.strName == 'strike1']
        strike3_temp = [v for v in mssnSitu.values() if v.strName == 'strike3']
        if len(strike2_temp) != 0:
            doctrine_2 = strike2_temp[0].get_doctrine()
            if target_huwei:
                geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
                for air in airs_strike2.values():
                    if '返回基地' in air.strActiveUnitStatus:
                        continue
                    doctrine = air.get_doctrine()
                    doctrine.set_emcon_according_to_superiors('no')
                    doctrine.set_em_control_status('Radar', 'Passive')
                    evade_ship(geopoint_target, air, doctrine_2)
            else:
                for air in airs_strike2.values():
                    air.return_to_base()
        if len(strike1_temp) != 0:
            doctrine_1 = strike1_temp[0].get_doctrine()
            if target_huwei:
                geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
                for air in airs_strike1.values():
                    if '返回基地' in air.strActiveUnitStatus:
                        continue
                    doctrine = air.get_doctrine()
                    doctrine.set_emcon_according_to_superiors('no')
                    doctrine.set_em_control_status('Radar', 'Passive')
                    evade_ship(geopoint_target, air, doctrine_1)
            else:
                for air in airs_strike1.values():
                    air.return_to_base()
        if len(strike3_temp) != 0:
            doctrine_3 = strike3_temp[0].get_doctrine()
            if target_huwei:
                geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
                for air in airs_strike3.values():
                    if '返回基地' in air.strActiveUnitStatus:
                        continue
                    doctrine = air.get_doctrine()
                    doctrine.set_emcon_according_to_superiors('no')
                    doctrine.set_em_control_status('Radar', 'Passive')
                    evade_ship(geopoint_target, air, doctrine_3)
            else:
                for air in airs_strike3.values():
                    air.return_to_base()
        return False
    # 'strike1'和61行，70行的'strike1'、'strike2'对应
    strkmssn_1 = [v for v in mssnSitu.values() if v.strName == 'strike1'][0]
    strkmssn_2 = [v for v in mssnSitu.values() if v.strName == 'strike2'][0]
    #多扇面攻击
    # strkmssn_1.set_auto_planner('true')
    # strkmssn_2.set_auto_planner('true')
    # edit_attack_throttle_for_strike(strike_mission=strkmssn_1)
    # edit_attack_throttle_for_strike(strike_mission=strkmssn_2)
    # 设置任务条令
    doctrine = strkmssn_1.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    # 3：是, 编组成员达到器状态武时离开编队返回基地
    if doctrine.m_WeaponStateRTB != 3:
        doctrine.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB
    # if doctrine.m_GunStrafeGroundTargets != 1:
    #     doctrine.gun_strafe_for_aircraft('1')  # m_GunStrafeGroundTargets
    if doctrine.m_BingoJokerRTB != 0:
        doctrine.set_fuel_state_for_air_group('3')  # m_BingoJokerRTB
        # 0， 对海目标自由开火
    # if doctrine.m_WCS_Surface != 0:
    #     doctrine.set_weapon_control_status('weapon_control_status_surface', '0')
    #     # 0， 对空目标自由开火
    # if doctrine.m_WCS_Air != 0:
    #     doctrine.set_weapon_control_status('weapon_control_status_air', '0')

    doctrine_2 = strkmssn_2.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    if doctrine_2.m_WeaponStateRTB != 3:
        doctrine_2.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB
    # if doctrine_2.m_GunStrafeGroundTargets != 1:
    #     doctrine_2.gun_strafe_for_aircraft('1')  # m_GunStrafeGroundTargets
    if doctrine_2.m_BingoJokerRTB != 0:
        doctrine_2.set_fuel_state_for_air_group('3')  # m_BingoJokerRTB
    # if doctrine_2.m_WCS_Surface != 0:
    #     doctrine_2.set_weapon_control_status('weapon_control_status_surface', '0')
    # if doctrine_2.m_WCS_Air != 0:
    #     doctrine_2.set_weapon_control_status('weapon_control_status_air', '0')

    patrol_missions_two = patrol_missions_2[0]
    patrol_doctrine_2 = patrol_missions_two.get_doctrine()
    patrol_doctrine_2.gun_strafe_for_aircraft('1')
    # strkPatrol = [v for v in patrol_missions_dic.values() if v.strName == 'strikePatrol']
    strkmssn3 = [v for v in mssnSitu.values() if 'strike3' in v.strName]
    missionUnits = patrol_missions_two.m_AssignedUnits.split('@')
    missionUnits_fight = [unit for unit in missionUnits if airs_dic[unit].strName != 'E-2K #1' and airs_dic[unit].strName != 'EC-130H #1']
    side_red = scenario.get_side_by_name('红方')
    airs = side_red.aircrafts
    airs_fight = [v for v in airs.values() if '米格' in v.strName]
    if len(airs_fight) < 2 and len(strkmssn3) == 0:
        print('把巡逻2任务换成对舰打击')
        strkmssn_3 = side.add_mission_strike('strike3', 2)
        strkmssn_3.set_flight_size(1)
        strkmssn_3.set_flight_size_check('false')
        ship_cor = []
        for k, v in target.items():
            strkmssn_3.assign_unit_as_target(k)
        for k, v in target.items():
            # strkmssn_3.assign_unit_as_target(k)
            ship_cor.append(v.dLatitude)
            ship_cor.append(v.dLongitude)
        # side.add_plan_way(0, 'strike3Way')
        # side.add_plan_way(0, 'strike3Way')
        side.add_plan_way(0, '航线2')
        side.add_plan_way(0, 'strike7Way')
        update_patrol_zone(side_name, scenario)
        update_support_zone_1(side_name, scenario)
        # latitude = '18.5488841549312', longitude = '124.272883564926'
        wayPointList1 = [{'latitude': 20.2139177649022, 'longitude': 123.50045418725},
                         {'latitude': 19.5518664351576, 'longitude': 124.05643194928},
                         {'latitude': 18.5488841549312, 'longitude': 124.272883564926}]
        cor_temp = [18.5488841549312, 124.272883564926]
        dis_ship_cor = get_horizontal_distance(ship_cor, cor_temp)
        # latitude = '18.6781283776856', longitude = '124.142326688987'
        if dis_ship_cor > 30:
            wayPointList1[2]['latitude'] += 0.0
            wayPointList1[2]['longitude'] += 0.0
        # for item in wayPointList1:
        #     side.add_plan_way_point('strike3Way', item['longitude'], item['latitude'])
        strkmssn_3.add_plan_way_to_mission(0, '航线2')
        utils.change_unit_mission(side, patrol_missions_two, strkmssn_3, missionUnits_fight)
        return_way_point_list = [{'latitude': 19.1561939434247, 'longitude': 123.841144249493},
                                 {'latitude': 19.6332044658959, 'longitude': 123.3016667523},
                                 {'latitude': 20.3441967218996, 'longitude': 122.835832334586}]
        for item in return_way_point_list:
            side.add_plan_way_point('strike7Way', item['longitude'], item['latitude'])
        strkmssn_3.add_plan_way_to_mission(2, 'strike7Way')
        # doctrine_strike3 = strkmssn_3.get_doctrine()
        # edit_anti_ship_weapon_doctrine(doctrine=doctrine_strike3)
        return False
    # airs_strike2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_4}
    # target_huwei = [v for k, v in contacts.items() if '护卫舰' in v.strName]
    # if target_huwei:
    #     geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
    #     for air in airs_strike2.values():
    #         evade_ship(geopoint_target, air, doctrine_2)
    return False


# 更新巡逻任务
def update_patrol_mission(side_name, scenario):
    print('开始更新巡逻任务')
    side = scenario.get_side_by_name(side_name)
    # 巡逻任务1,2飞机飞行的路线设置的航路点
    xl1_lat = 0
    xl1_lon = 0
    xl2_lat = 0
    xl2_lon = 0
    # latitude = '21.8030724732456', longitude = '121.421512081102'
    # latitude = '21.8484145390819', longitude = '122.360241762715'
    for point in side.referencepnts.values():
        if point.strName == side_name + 'rp1':
            xl1_lat = point.dLatitude
            xl1_lon = point.dLongitude
        elif point.strName == 'RP-3678':
            xl2_lat = point.dLatitude
            xl2_lon = point.dLongitude

    airs_dic = side.aircrafts

    # 执行任务的飞机,
    airs = {k: v for k, v in airs_dic.items() if v.strName in lst_1 or v.strName in lst_2}

    # 获取巡逻任务，如果巡逻任务为0，说明还没有，创建巡逻任务。
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    if len(patrol_missions) == 0:
        return False

    point_prosecution_list = creat_prosecution_area(side_name, scenario)
    ps_str = []
    for ps in point_prosecution_list:
        for name in ps:
            ps_str.append(name.strName)
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
            # 5,6,7号飞机
            airs_xl1 = {k: airs[k] for k, v in airs.items() if v.strName in lst_1}
            patrol_mission.assign_units(airs_xl1)
            patrol_mission.set_flight_size(2)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            # patrol_mission.set_throttle_transit('Cruise')
            edit_thort_doctrine(patrol_mission)
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
        if dis <= 150:
            mission_doctrine.ignore_plotted_course('yes')
            # genpoint_away = get_end_point(geopoint_air, 15, (air.fCurrentHeading + 150))
            # hwj latitude = '19.3658915786203', longitude = '125.001816638868'
            # latitude = '19.2323017102236', longitude = '125.170486962517'
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
        # i += 1
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
    # latitude = '21.6701551543473', longitude = '122.35337044599'
    # latitude = '21.6698815188537', longitude = '122.741326377829'
    # point_1 = [(22.181378549063, 121.049571002033), (22.1691773335694, 124.194508316028),
    #            (20.6722068167905, 121.062131270682), (20.6370176672735, 124.156690488837)]
    # latitude = '21.813803192903', longitude = '122.369519984786'
    # latitude = '21.8326948541021', longitude = '122.521524522641'
    # latitude = '21.6821653996223', longitude = '122.531658874429'
    # latitude = '21.6914739156693', longitude = '122.349410016875'
    point_1 = [(21.8210656716398, 122.356667127581), (21.8752434450009, 122.768058783733),
               (21.6698815188537, 122.741326377829), (21.6701551543473, 122.35337044599)]
    point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
               (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
    # latitude = '21.8007722911492', longitude = '121.891366599536'
    # latitude = '21.8133512145801', longitude = '121.999449321817' latitude='21.8070791085451', longitude='121.992694229762'
    # latitude = '21.6941810340043', longitude = '122.006199822804' latitude='21.7067271871263', longitude='121.992700378373' latitude='21.6816366869856', longitude='122.012945762659'
    # latitude = '21.7066982331022', longitude = '121.898190784059'
    # point_1 = [(21.8007722911492, 121.891366599536), (21.8133512145801, 121.999449321817),
    #            (21.6941810340043, 122.006199822804), (21.7066982331022, 121.898190784059)]
    # lat: 纬度， lon：经度
    # xl1
    rp1 = side.add_reference_point(side_name + 'rp1', point_1[0][0], point_1[0][1])
    rp2 = side.add_reference_point(side_name + 'rp2', point_1[1][0], point_1[1][1])
    rp3 = side.add_reference_point(side_name + 'rp3', point_1[2][0], point_1[2][1])
    rp4 = side.add_reference_point(side_name + 'rp4', point_1[3][0], point_1[3][1])
    point_list.append([rp1, rp2, rp3, rp4])

    return point_list

# 另写一个创建巡逻区，这次把两个巡逻任务分开执行，试试效果
def create_patrol_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # point_1 = [(22.181378549063, 121.049571002033), (22.1691773335694, 124.194508316028),
    #            (20.6722068167905, 121.062131270682), (20.6370176672735, 124.156690488837)]
    point_1 = [(21.8210656716398,122.356667127581),(21.8752434450009,122.768058783733),
               (21.6236431494821,123.354562698353),(21.5245647261449,122.005001630342)]
    point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
               (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
    # point_1 = [(21.8007722911492, 121.891366599536), (21.8133512145801, 121.999449321817),
    #            (21.6941810340043, 122.006199822804), (21.7066982331022, 121.898190784059)]
    # lat: 纬度， lon：经度
    # xl1
    rp9 = side.add_reference_point(side_name + 'rp9', point_1[0][0], point_1[0][1])
    rp10 = side.add_reference_point(side_name + 'rp10', point_1[1][0], point_1[1][1])
    rp11 = side.add_reference_point(side_name + 'rp11', point_1[2][0], point_1[2][1])
    rp12 = side.add_reference_point(side_name + 'rp12', point_1[3][0], point_1[3][1])
    point_list.append([rp9, rp10, rp11, rp12])
    return point_list

# 设置警戒区的区域
def creat_prosecution_area(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # latitude = '22.1593596923231', longitude = '121.147008976371'
    # latitude = '22.5329177785997', longitude = '123.746663413981'
    # latitude = '21.2291643151066', longitude = '121.162975576448'
    # latitude = '21.705618145078', longitude = '123.70585754102'
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981),
               (21.705618145078,123.70585754102), (21.2291643151066,121.162975576448)]
    rp5 = side.add_reference_point(side_name + 'rp5', point_1[0][0], point_1[0][1])
    rp6 = side.add_reference_point(side_name + 'rp6', point_1[1][0], point_1[1][1])
    rp7 = side.add_reference_point(side_name + 'rp7', point_1[2][0], point_1[2][1])
    rp8 = side.add_reference_point(side_name + 'rp8', point_1[3][0], point_1[3][1])
    point_list.append([rp5, rp6, rp7, rp8])
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
    patrol_mission.set_throttle_transit('Cruise')
    patrol_mission.set_throttle_station('Cruise')
    patrol_mission.set_throttle_attack('Cruise')
    patrol_mission.set_transit_altitude(13000.0)
    patrol_mission.set_station_altitude(13000.0)

def update_patrol_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    point_1 = [(20.5733193239388, 123.784279150979), (20.5203738136706, 124.109096192867),
               (20.2612650808583, 123.638980121306), (20.2542841769267, 124.028042616076)]
    # latitude = '20.5733193239388', longitude = '123.784279150979'
    # latitude = '20.5203738136706', longitude = '124.109096192867'
    # latitude = '20.2612650808583', longitude = '123.638980121306'
    # latitude = '20.2542841769267', longitude = '124.028042616076'
    # latitude='20.8612760556798', longitude='122.97096027272'
    # latitude = '20.89954721661', longitude = '123.18875736993'
    # latitude = '20.7359032286196', longitude = '122.92736887149'
    # latitude = '20.7431007450093', longitude = '123.145339607124'

    point_2 = [(20.8612760556798,122.97096027272),(20.89954721661,123.18875736993),
               (20.7431007450093,123.145339607124), (20.7359032286196,122.92736887149)]
    # latitude = '19.4160587709569', longitude = '124.09363622386'
    # latitude = '19.4105092550855', longitude = '124.22959286376'
    # latitude = '19.3380359651572', longitude = '124.188222632691'
    # latitude = '19.3547316753547', longitude = '124.093676542387'
    point_2 = [(19.4160587709569, 124.09363622386), (19.4105092550855, 124.22959286376),
               (19.3380359651572, 124.188222632691), (19.3547316753547, 124.093676542387)]
    # latitude = '19.8452434017736', longitude = '124.15306856036'
    # latitude = '19.8608816443815', longitude = '124.258533532556'
    # latitude = '19.7773499598268', longitude = '124.258482921611'
    # latitude = '19.756491023618', longitude = '124.16971312762'
    point_2 = [(19.8452434017736, 124.15306856036), (19.8608816443815, 124.258533532556),
               (19.7773499598268, 124.258482921611), (19.756491023618, 124.16971312762)]
    side.set_reference_point(side_name + 'rp1', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp2', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp3', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp4', point_2[3][0], point_2[3][1])

# 给3个对海打击任务设置油门，试试效果
def edit_attack_throttle_for_strike(strike_mission):
    strike_mission.set_throttle('attackThrottleAircraft', 'Flank')
    # 老版的接口有，现在没有了
    # strike_mission.set_speed('attackSpeedAircraft',1700.0)
# 新增预警机和干扰机支援任务的区域
def support_zone_for_two(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # latitude = '21.8764427622847', longitude = '121.330904108449'
    # latitude = '21.8335734773605', longitude = '121.478618597081'
    # latitude = '21.6920926322308', longitude = '121.580152213845'
    # latitude = '21.6899037180596', longitude = '121.405076571889'
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
    # latitude = '22.4098475117646', longitude = '122.186072181501'
    # latitude = '22.418764139488', longitude = '122.367143273071'
    # latitude = '22.233752742808', longitude = '122.386191481229'
    # latitude = '22.2336414046035', longitude = '122.186317353378'

    point_1 = [(22.4098475117646, 122.186072181501), (22.418764139488, 122.367143273071),
               (22.233752742808, 122.386191481229), (22.2336414046035, 122.186317353378)]
    rp20 = side.add_reference_point(side_name + 'rp20', point_1[0][0], point_1[0][1])
    rp21 = side.add_reference_point(side_name + 'rp21', point_1[1][0], point_1[1][1])
    rp22 = side.add_reference_point(side_name + 'rp22', point_1[2][0], point_1[2][1])
    rp23 = side.add_reference_point(side_name + 'rp23', point_1[3][0], point_1[3][1])
    point_list.append([rp20, rp21, rp22, rp23])
    return point_list
# 更新预警机支援的区域
def update_support_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_2 = [(20.8612760556798, 122.97096027272), (20.89954721661, 123.18875736993),
               (20.7431007450093, 123.145339607124), (20.7359032286196, 122.92736887149)]
    point_2 = [(19.4160587709569, 124.09363622386), (19.4105092550855, 124.22959286376),
               (19.3380359651572, 124.188222632691), (19.3547316753547, 124.093676542387)]
    point_2 = [(19.8452434017736, 124.15306856036), (19.8608816443815, 124.258533532556),
               (19.7773499598268, 124.258482921611), (19.756491023618, 124.16971312762)]
    side.set_reference_point(side_name + 'rp15', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp16', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp17', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp18', point_2[3][0], point_2[3][1])
