# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
# from blue_agent_lj.blue_agent_lj_comprehensive_skill.utils import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
# F18
# lst_1 = ['Udoshi #1', 'Udoshi #2']
# lst_2 = ['Udoshi #3', 'Udoshi #4', 'Udoshi #5', 'Udoshi #6', ]
# lst_3 = ['Udoshi #7', 'Udoshi #8', 'Udoshi #9', 'Udoshi #10']
lst_1 = ['Udoshi #1', 'Udoshi #2', 'Udoshi #3', 'Udoshi #4', 'Udoshi #5', 'Udoshi #6', 'Udoshi #7', 'Udoshi #8']
lst_4 = ['Champion #1', 'Champion #2', 'Champion #3', 'Champion #4', 'Champion #5', 'Champion #6', 'Champion #7']
# grj
lst_5 = ['Shrike #1']
lst_6 = ['Shrike #2']
# yjj
lst_7 = ['Hornet #1']
lst_8 = ['Hornet #2']

# 下面这几架飞机用于接收从外部传过来的任务
lst_9 = ['Udoshi #9', 'Udoshi #10', 'Champion #8']
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
    if len(airs) <= 40:
        return True
    else:
        return False


#
def create_antisurfaceship_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs_1 = {k: v for k, v in airs_dic.items() if v.strName in lst_4}
    contacts = side.contacts
    target_list = [v.strName for v in contacts.values()]
    print('target_list=',target_list)
    targets = {k: v for k, v in contacts.items() if ('052D' in v.strName)}
    for k, v in targets.items():
        # set_mark_contact设置目标对抗关系,H is 敌方
        side.set_mark_contact(k, 'H')
    mssnSitu = side.strikemssns
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions_2 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '2']
    patrol_missions_two = patrol_missions_2[0]
    missionUnits = patrol_missions_two.m_AssignedUnits.split('@')
    missionUnits_fight = [unit for unit in missionUnits]
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
        strkmssn_1 = side.add_mission_strike('strike1', 2)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_1.set_flight_size(1)
        strkmssn_1.set_flight_size_check('false')
    else:
        return False
    # strkmssn_1.assign_units(airs_1)
    for k, v in targets.items():
        strkmssn_1.assign_unit_as_target(k)
    # 通过 ctrl +x 拿到航线设置的点
    side.add_plan_way(0, 'strike1Way')

    # 增加两个返航航线,strike5Way
    side.add_plan_way(0, 'strike5Way')
    # 试试这组点
    # latitude = '24.7899945352548', longitude = '125.677297602663'
    # latitude = '25.8099824789415', longitude = '124.689932555361'
    # latitude = '26.6766753892229', longitude = '122.732505098363'
    wayPointList2 = [{'latitude': 24.7899945352548, 'longitude': 125.677297602663},
                     {'latitude': 25.8099824789415, 'longitude': 124.689932555361},
                     {'latitude': 26.6766753892229, 'longitude': 122.732505098363}]
    for item in wayPointList2:
        side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
    strkmssn_1.add_plan_way_to_mission(0, 'strike1Way')
    utils.change_unit_mission(side, patrol_missions_two, strkmssn_1, missionUnits_fight)

    # 试试这组返航航线
    # latitude = '23.7566654449342', longitude = '123.967887489896'
    # latitude = '24.3883913808073', longitude = '122.41387521244'
    # latitude = '25.9840653538193', longitude = '122.137323430458'
    # return_way_point_list = [{'latitude': 25.9840653538193, 'longitude': 122.137323430458},
    #                          {'latitude': 24.3883913808073, 'longitude': 122.41387521244},
    #                          {'latitude': 23.7566654449342, 'longitude': 123.967887489896}]
    # for item in return_way_point_list:
    #     side.add_plan_way_point('strike5Way', item['longitude'], item['latitude'])
    # strkmssn_1.add_plan_way_to_mission(2, 'strike5Way')
    return False

# 更新反舰打击任务
def update_antisurfaceship_mission(side_name, scenario):
    print('开始更新反舰任务和巡逻2任务')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    contacts = side.contacts
    # target = {k: v for k, v in contacts.items() if '航空母舰' in v.strName}
    target = {k: v for k, v in contacts.items() if '护卫舰' in v.strName}

    mssnSitu = side.strikemssns
    strkmssn = [v for v in mssnSitu.values() if 'strike' in v.strName]
    if len(strkmssn) != 1:
        return False
    strkmssn_1 = [v for v in mssnSitu.values() if v.strName == 'strike1'][0]
    # 设置任务条令
    doctrine = strkmssn_1.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    # 3：是, 编组成员达到器状态武时离开编队返回基地
    if doctrine.m_WeaponStateRTB != 3:
        doctrine.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB

    if doctrine.m_BingoJokerRTB != 0:
        doctrine.set_fuel_state_for_air_group('3')  # m_BingoJokerRTB
    # airs_strike2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_4}
    # target_052 = [v for k, v in contacts.items() if '052D' in v.strName]
    # if target_052:
    #     geopoint_target = (target_052[0].dLatitude, target_052[0].dLongitude)
    #     for air in airs_strike2.values():
    #         evade_ship(geopoint_target, air, doctrine)
    return False


# 更新巡逻任务
def update_patrol_mission(side_name, scenario):
    print('开始更新巡逻任务')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    ships_dic = side.ships
    # 执行任务的飞机,
    airs = {k: v for k, v in airs_dic.items() if v.strName in lst_1}
    airs_1 = {k: v for k, v in airs_dic.items() if v.strName in lst_4}
    airs_one = {k: v for k, v in airs_dic.items() if v.strName in ['Udoshi #8']}
    # 获取巡逻任务，如果巡逻任务为0，说明还没有，创建巡逻任务。
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    if len(patrol_missions) == 0:
        return False
    air_cor_point_list = []
    for k, v in airs_one.items():
        air_cor_point_list.append(v.dLatitude)
        air_cor_point_list.append(v.dLongitude)
    cor_temp = [26.138850196947, 123.910817093635]
    if len(air_cor_point_list) != 0:
        dis_ship_cor = get_horizontal_distance(air_cor_point_list, cor_temp)
        print('dis_ship_cor=',dis_ship_cor)
        if dis_ship_cor < 300:
            update_support_zone_1(side_name, scenario)
    point_prosecution_list = creat_prosecution_area(side_name, scenario)
    ps_str = []
    for ps in point_prosecution_list:
        for name in ps:
            ps_str.append(name.strName)
    point_prosecution_list_ship = creat_prosecution_area_ship(side_name, scenario)
    ps_str_ship = []
    for ps in point_prosecution_list_ship:
        for name in ps:
            ps_str_ship.append(name.strName)
    # 如果有任务，就每个任务更新，包含给任务分配飞机，1/3规则
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + 'xl1':
            patrol_mission.set_prosecution_zone(ps_str)
            doctrine_xl1 = patrol_mission.get_doctrine()
            doctrine_xl1.set_weapon_state_for_aircraft(2002)
            doctrine_xl1.set_weapon_state_for_air_group('3')
            doctrine_xl1.gun_strafe_for_aircraft('1')
            edit_weapon_doctrine(doctrine=doctrine_xl1)
            airs_xl1 = {k: airs[k] for k, v in airs.items()}
            patrol_mission.assign_units(airs_xl1)
            patrol_mission.set_flight_size(2)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
        elif patrol_mission.strName == side_name + 'xl2':
            patrol_mission.set_prosecution_zone(ps_str)
            doctrine_xl1 = patrol_mission.get_doctrine()
            doctrine_xl1.set_weapon_state_for_aircraft(2002)
            doctrine_xl1.set_weapon_state_for_air_group('3')
            doctrine_xl1.gun_strafe_for_aircraft('1')
            edit_weapon_doctrine(doctrine=doctrine_xl1)
            # airs_xl1 = {k: airs[k] for k, v in airs.items()}
            patrol_mission.assign_units(airs_1)
            patrol_mission.set_flight_size(2)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
        elif patrol_mission.strName == side_name + 'fsmxl1':
            patrol_mission.set_prosecution_zone(ps_str_ship)
            patrol_mission.assign_units(ships_dic)
            patrol_mission.set_flight_size(1)
            patrol_mission.set_flight_size_check('false')
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
    # 更新支援任务，设置条令
    support_missions_dic = side.get_support_missions()
    support_missions_1 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '1']
    airs_support1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_5}
    airs_support2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_6}
    airs_support3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_7}
    if len(support_missions_1) != 0:
        for air in airs_support1.values():
            doctrine = air.get_doctrine()
            # doctrine.set_em_control_status('Radar', 'Active')
            doctrine.set_em_control_status('OECM', 'Active')
    support_missions_2 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '2']
    if len(support_missions_2) != 0:
        for air in airs_support2.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
            # doctrine.set_em_control_status('Radar', 'Active')
    support_missions_3 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '3']
    if len(support_missions_3) != 0:
        for air in airs_support3.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('Radar', 'Active')
    return False

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
    for point in point_list:
        point_str = []
        for name in point:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + 'xl' + str(1)

        # 创建巡逻任务，设置1/3规则
        patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str)
        print('巡逻任务已创建')
        patrolmssn.set_one_third_rule('false')
        patrolmssn.set_patrol_zone(point_str)
        # side.add_plan_way(0, 'strike9Way')
        # # latitude = '23.4954903057241', longitude = '123.849199692431'
        # # latitude = '24.1757011331708', longitude = '121.883488208345'
        # # latitude = '25.286532190074', longitude = '121.118809412332'
        # way_point_list = [{'latitude': 23.4954903057241, 'longitude': 123.849199692431},
        #                          {'latitude': 24.1757011331708, 'longitude': 121.883488208345},
        #                          {'latitude': 25.286532190074, 'longitude': 121.118809412332}]
        # for item in way_point_list:
        #     side.add_plan_way_point('strike9Way', item['longitude'], item['latitude'])
        # patrolmssn.add_plan_way_to_mission(0, 'strike9Way')
        patrolmssn.set_start_time('2022-10-8 13:05:00')
        # i += 1
    # 设置第二个巡逻任务
    point_list_1 = create_patrol_zone_1(side_name, scenario)
    for point in point_list_1:
        point_str = []
        for name in point:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + 'xl' + str(2)

        # 创建巡逻任务，设置1/3规则
        patrolmssn_1 = side.add_mission_patrol(patrol_name, 0, point_str)
        print('巡逻任务已创建')
        patrolmssn_1.set_one_third_rule('false')
        patrolmssn_1.set_patrol_zone(point_str)
        patrolmssn_1.set_start_time('2022-10-8 13:20:00')
    # 给船下个反水面巡逻任务，让船往下跑，躲避敌方船发的导弹
    point_list_ship = create_patrol_zone_ship(side_name, scenario)
    for point in point_list_ship:
        point_str = []
        for name in point:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + 'fsmxl' + str(1)

        # 创建巡逻任务，设置1/3规则
        patrolmssn_ship = side.add_mission_patrol(patrol_name, 1, point_str)
        print('反水面巡逻任务已创建')
        patrolmssn_ship.set_one_third_rule('false')
        patrolmssn_ship.set_patrol_zone(point_str)
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
        supportmssn.assign_units(airs_support3)
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
        supportmssn.assign_units(airs_support2)
        supportmssn.set_one_third_rule('false')
        supportmssn.set_flight_size(1)
        supportmssn.set_flight_size_check('false')

    scenario.mozi_server.set_key_value(f'{side_name}巡逻任务已创建', 'Yes')
    return False

# 巡逻区域经纬度的生成
def create_patrol_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # latitude = '26.3455211646726', longitude = '123.679503013611'
    # latitude = '26.3459438070089', longitude = '123.924596166515'
    # latitude = '26.138850196947', longitude = '123.910817093635'
    # latitude = '26.1384553584977', longitude = '123.694098104093'
    # latitude = '25.6116881713478', longitude = '124.964210157727'
    # latitude = '25.6003012141341', longitude = '125.097154575031'
    # latitude = '25.4871463915998', longitude = '125.091251416978'
    # latitude = '25.4922773303988', longitude = '124.965482221906'
    # point_1 = [(26.3455211646726, 123.679503013611), (26.3459438070089, 123.924596166515),
    #            (26.138850196947, 123.910817093635), (26.1384553584977, 123.694098104093)]
    point_1 = [(25.6116881713478, 124.964210157727), (25.6003012141341, 125.097154575031),
               (25.4871463915998, 125.091251416978), (25.4922773303988, 124.965482221906)]
    rp1 = side.add_reference_point(side_name + 'rp1', point_1[0][0], point_1[0][1])
    rp2 = side.add_reference_point(side_name + 'rp2', point_1[1][0], point_1[1][1])
    rp3 = side.add_reference_point(side_name + 'rp3', point_1[2][0], point_1[2][1])
    rp4 = side.add_reference_point(side_name + 'rp4', point_1[3][0], point_1[3][1])
    point_list.append([rp1, rp2, rp3, rp4])

    return point_list

# 另写一个创建巡逻区，试试效果
def create_patrol_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(25.6116881713478, 124.964210157727), (25.6003012141341, 125.097154575031),
               (25.4871463915998, 125.091251416978), (25.4922773303988, 124.965482221906)]
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
    # latitude = '26.8849337179684', longitude = '123.550983489887'
    # latitude = '26.8723734074874', longitude = '124.536196875402'
    # latitude = '25.3457510280031', longitude = '124.530377330276'
    # latitude = '25.3457509055187', longitude = '123.556866367378'
    point_1 = [(26.8849337179684, 123.550983489887), (26.8723734074874, 124.536196875402),
               (25.3457510280031, 124.530377330276), (25.3457509055187, 123.556866367378)]
    point_1 = [(25.6116881713478, 124.964210157727), (25.6003012141341, 125.097154575031),
               (25.4871463915998, 125.091251416978), (25.4922773303988, 124.965482221906)]
    rp5 = side.add_reference_point(side_name + 'rp5', point_1[0][0], point_1[0][1])
    rp6 = side.add_reference_point(side_name + 'rp6', point_1[1][0], point_1[1][1])
    rp7 = side.add_reference_point(side_name + 'rp7', point_1[2][0], point_1[2][1])
    rp8 = side.add_reference_point(side_name + 'rp8', point_1[3][0], point_1[3][1])
    point_list.append([rp5, rp6, rp7, rp8])
    return point_list

# 用于巡逻任务中编辑武器条令,空空弹武器条例
def edit_weapon_doctrine(doctrine):

    doctrine.set_weapon_release_authority('51', '1999', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('51', '2000', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('51', '2001', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('51', '2002', '2', '1', '80', 'none', 'false')
    # doctrine.set_weapon_release_authority('718', '2021', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('51', '2031', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('51', '2100', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('51', '2200', '2', '1', '80', 'none', 'false')

    doctrine.set_weapon_release_authority('945', '1999', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2000', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2001', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2002', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2021', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2031', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2100', '2', '1', '80', 'none', 'false')
    doctrine.set_weapon_release_authority('945', '2200', '2', '1', '80', 'none', 'false')


def update_patrol_zone(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    point_2 = [(19.8452434017736, 124.15306856036), (19.8608816443815, 124.258533532556),
               (19.7773499598268, 124.258482921611), (19.756491023618, 124.16971312762)]
    side.set_reference_point(side_name + 'rp1', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp2', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp3', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp4', point_2[3][0], point_2[3][1])


# 新增预警机和干扰机支援任务的区域
def support_zone_for_two(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(24.5630917651986, 125.698087741808), (24.5328699592565, 126.149042036246),
               (24.0978161998088, 126.13106994995), (24.0966677391708, 125.71563636583)]
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
    point_1 = [(24.5630917651986, 125.698087741808), (24.5328699592565, 126.149042036246),
               (24.0978161998088, 126.13106994995), (24.0966677391708, 125.71563636583)]
    rp20 = side.add_reference_point(side_name + 'rp20', point_1[0][0], point_1[0][1])
    rp21 = side.add_reference_point(side_name + 'rp21', point_1[1][0], point_1[1][1])
    rp22 = side.add_reference_point(side_name + 'rp22', point_1[2][0], point_1[2][1])
    rp23 = side.add_reference_point(side_name + 'rp23', point_1[3][0], point_1[3][1])
    point_list.append([rp20, rp21, rp22, rp23])
    return point_list
# 更新预警机支援的区域
def update_support_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    # latitude = '25.1618173202016', longitude = '121.427656166545'
    # latitude = '25.1869739965192', longitude = '121.725346071621'
    # latitude = '24.8756449892155', longitude = '121.721139096876'
    # latitude = '24.8775920350867', longitude = '121.453260307804'
    # latitude = '25.9451923372157', longitude = '124.241880351634'
    # latitude = '25.9491888278148', longitude = '124.350646427266'
    # latitude = '25.855061856555', longitude = '124.351306051816'
    # latitude = '25.8684333305265', longitude = '124.234730648022'
    # latitude = '25.3005074442772', longitude = '125.322822803084'
    # latitude = '25.31394102605', longitude = '125.447990979471'
    # latitude = '25.1883681048325', longitude = '125.462652465827'
    # latitude = '25.1748636904787', longitude = '125.330646666097'
    point_2 = [(25.3005074442772, 125.322822803084), (25.31394102605, 125.447990979471),
               (25.1883681048325, 125.462652465827), (25.1748636904787, 125.330646666097)]
    side.set_reference_point(side_name + 'rp15', point_2[0][0], point_2[0][1])
    side.set_reference_point(side_name + 'rp16', point_2[1][0], point_2[1][1])
    side.set_reference_point(side_name + 'rp17', point_2[2][0], point_2[2][1])
    side.set_reference_point(side_name + 'rp18', point_2[3][0], point_2[3][1])

def create_patrol_zone_ship(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # latitude = '24.5630917651986', longitude = '125.698087741808'
    # latitude = '24.5328699592565', longitude = '126.149042036246'
    # latitude = '24.0978161998088', longitude = '126.13106994995'
    # latitude = '24.0966677391708', longitude = '125.71563636583'
    point_1 = [(24.5630917651986, 125.698087741808), (24.5328699592565, 126.149042036246),
               (24.0978161998088, 126.13106994995), (24.0966677391708, 125.71563636583)]
    rp24 = side.add_reference_point(side_name + 'rp24', point_1[0][0], point_1[0][1])
    rp25 = side.add_reference_point(side_name + 'rp25', point_1[1][0], point_1[1][1])
    rp26 = side.add_reference_point(side_name + 'rp26', point_1[2][0], point_1[2][1])
    rp27 = side.add_reference_point(side_name + 'rp27', point_1[3][0], point_1[3][1])
    point_list.append([rp24, rp25, rp26, rp27])

    return point_list

def creat_prosecution_area_ship(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(24.5630917651986, 125.698087741808), (24.5328699592565, 126.149042036246),
               (24.0978161998088, 126.13106994995), (24.0966677391708, 125.71563636583)]
    rp28 = side.add_reference_point(side_name + 'rp28', point_1[0][0], point_1[0][1])
    rp29 = side.add_reference_point(side_name + 'rp29', point_1[1][0], point_1[1][1])
    rp30 = side.add_reference_point(side_name + 'rp30', point_1[2][0], point_1[2][1])
    rp31 = side.add_reference_point(side_name + 'rp31', point_1[3][0], point_1[3][1])
    point_list.append([rp28, rp29, rp30, rp31])
    return point_list
# 躲避护卫舰接口
def evade_ship(geopoint_target, air, mission_doctrine):
    geopoint_air = (air.dLatitude, air.dLongitude)
    if geopoint_target:
        dis = get_horizontal_distance(geopoint_air, geopoint_target)
        if dis <= 100:
            mission_doctrine.ignore_plotted_course('yes')
            # latitude = '25.879565581978', longitude = '122.604033159999'
            # latitude = '25.6434439791198', longitude = '122.08132608406'
            genpoint_away = (geopoint_target[0] - 0.23, geopoint_target[1] - 0.6)
            # genpoint_away_1 = (geopoint_target[0] - 0.18, geopoint_target[1] - 0.1)
            # genpoint_away_2 = (geopoint_target[0] + 0.18, geopoint_target[1] + 0.18)
            air.plot_course([genpoint_away])

# 根据接收到信号，判断新建哪个指令
def judge_mission_type(side_name, scenario, mission_type):
    side = scenario.get_side_by_name(side_name)

# 根据接收到信号，执行从外部传过来的指令
def create_new_patrol_mission(side_name, scenario, new_air_name, new_patrol_point):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs = {k: v for k, v in airs_dic.items() if v.strName in new_air_name}
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}从外部接收新的巡逻任务已创建')
    if flag is not 'Yes':
        new_point_list = create_new_patrol_zone(side_name, scenario, new_patrol_point)
        new_point_prosecution_list = creat_new_prosecution_area(side_name, scenario, new_patrol_point)
        patrol_name = side_name + 'new_xl' + str(1)
        # 创建巡逻任务，设置1/3规则
        patrolmssn = side.add_mission_patrol(patrol_name, 0, new_point_list)

        print('新巡逻任务已创建')
        patrolmssn.set_one_third_rule('false')
        patrolmssn.set_patrol_zone(new_point_list)
        patrolmssn.set_prosecution_zone(new_point_prosecution_list)
        patrolmssn.set_is_active('true')
        patrolmssn.assign_units(airs)
        patrolmssn.set_flight_size(2)
        patrolmssn.set_flight_size_check('false')
        patrolmssn.set_opa_check('true')
        patrolmssn.set_wwr_check('true')
        patrolmssn.set_emcon_usage('false')
        scenario.mozi_server.set_key_value(f'{side_name}从外部接收新的巡逻任务已创建', 'Yes')
# 创建新巡逻任务的巡逻区
def create_new_patrol_zone(side_name, scenario, new_patrol_point):
    side = scenario.get_side_by_name(side_name)
    central_lat, central_lon = new_patrol_point
    point_list = []
    side.add_reference_point(side_name + 'new_xl_point1', central_lat + 0.03, central_lon - 0.05)
    side.add_reference_point(side_name + 'new_xl_point2', central_lat + 0.04, central_lon + 0.06)
    side.add_reference_point(side_name + 'new_xl_point3', central_lat - 0.04, central_lon + 0.05)
    side.add_reference_point(side_name + 'new_xl_point4', central_lat - 0.03, central_lon - 0.06)
    point_list.append(side_name + 'new_xl_point1')
    point_list.append(side_name + 'new_xl_point2')
    point_list.append(side_name + 'new_xl_point3')
    point_list.append(side_name + 'new_xl_point4')
    return point_list
# 创建新巡逻任务的警戒区
def creat_new_prosecution_area(side_name, scenario, new_patrol_point):
    side = scenario.get_side_by_name(side_name)
    central_lat, central_lon = new_patrol_point
    point_list = []
    side.add_reference_point(side_name + 'new_xl_jj_point1', central_lat + 0.13, central_lon - 0.15)
    side.add_reference_point(side_name + 'new_xl_jj_point2', central_lat + 0.14, central_lon + 0.16)
    side.add_reference_point(side_name + 'new_xl_jj_point3', central_lat - 0.14, central_lon + 0.15)
    side.add_reference_point(side_name + 'new_xl_jj_point4', central_lat - 0.13, central_lon - 0.16)
    point_list.append(side_name + 'new_xl_jj_point1')
    point_list.append(side_name + 'new_xl_jj_point2')
    point_list.append(side_name + 'new_xl_jj_point3')
    point_list.append(side_name + 'new_xl_jj_point4')
    return point_list

# 根据接收到信号，执行从外部传过来的指令,创建新的空对舰任务
def create_new_strike_mission(side_name, scenario, new_air_name, new_target):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    contacts = side.contacts
    airs_strike = {k: v for k, v in airs_dic.items() if v.strName in new_air_name}
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}从外部接收新的对舰任务已创建')
    strike_name = side_name + 'new_strike' + str(1)
    if flag is not 'Yes':
        strkmssn_1 = side.add_mission_strike(strike_name, 2)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_1.set_one_third_rule('false')
        strkmssn_1.set_flight_size(1)
        strkmssn_1.set_flight_size_check('false')
        targets = {k: v for k, v in contacts.items() for ship_name in new_target if ship_name in v.strName}
        for k, v in targets.items():
            # set_mark_contact设置目标对抗关系,H is 敌方
            side.set_mark_contact(k, 'H')
        for k, v in targets.items():
            strkmssn_1.assign_unit_as_target(k)
        strkmssn_1.assign_units(airs_strike)
        strike_plot_name = 'new_strikeway2'
        strike_plot_point_list = [{'latitude': 24.7899945352548, 'longitude': 125.677297602663},
                     {'latitude': 25.8099824789415, 'longitude': 124.689932555361},
                     {'latitude': 26.6766753892229, 'longitude': 122.732505098363}]
        side.add_plan_way(0, strike_plot_name)
        for item in strike_plot_point_list:
            side.add_plan_way_point(strike_plot_name, item['longitude'], item['latitude'])
        strkmssn_1.add_plan_way_to_mission(0, strike_plot_name)
        scenario.mozi_server.set_key_value(f'{side_name}从外部接收新的对舰任务已创建', 'Yes')



