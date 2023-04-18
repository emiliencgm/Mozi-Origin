# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission

# lst = ['闪电 #5', '闪电 #6', '闪电 #7', '闪电 #8', '闪电 #9', '闪电 #10', '闪电 #11', '闪电 #12', '闪电 #13', '闪电 #14', '闪电 #15',
#        '闪电 #16']
lst_1 = ['F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','EC-130H #2']
lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9', 'EC-130H #1', 'E-2K #1']
# lst_1 = ['F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9']
# lst_2 = ['EC-130H #2', 'EC-130H #1', 'E-2K #1']
lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04']
lst_4 = ['F-16A #1', 'F-16A #2','F-16A #3', 'F-16A #4']


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
        for point in side.referencepnts.values():
            if point.strName == 'RP-3678':
                xl2_lat = point.dLatitude
                xl2_lon = point.dLongitude

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
            Patrolmssn2.set_flight_size(2)
            Patrolmssn2.set_flight_size_check('false')
            Patrolmssn2.set_opa_check('true')
            Patrolmssn2.set_wwr_check('true')
            Patrolmssn2.set_emcon_usage('false')
            for air in airs_xl2.values():
                if air:
                    # print('air2', air.strName)
                    # air.get_valid_weapon_load()
                    if '返回基地' in air.strActiveUnitStatus:
                        continue
                    # 航路点设置
                    # air.plot_course([(xl2_lat, xl2_lon)])
                    if air.strName == 'EC-130H #1':
                        doctrine = air.get_doctrine()
                        doctrine.set_em_control_status('OECM', 'Active')
                        # air.plot_course([(xl2_lat + 1, xl2_lon - 0.2)])
                    if air.strName == 'E-2K #1':
                        doctrine = air.get_doctrine()
                        doctrine.set_em_control_status('Radar', 'Active')
                        # air.plot_course([(xl2_lat + 1, xl2_lon - 0.2)])

    side_red = scenario.get_side_by_name('红方')
    airs = side_red.aircrafts
    if len(airs) <= 10:
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
        target_2 = {k: v for k, v in contacts.items() if ('驱逐舰' in v.strName)}
        for k, v in targets.items():
            # set_mark_contact设置目标对抗关系,H is 敌方
            side.set_mark_contact(k, 'H')
        mssnSitu = side.strikemssns
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
            strkmssn_1 = side.add_mission_strike('strike1', 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_1.set_flight_size_check('false')
        else:
            return False
        # 根据敌方护卫舰的位置创建打击行动航线，试试效果
        way_point_list_1 = []
        way_point_dict_1_1 = {}
        way_point_dict_1_2 = {}
        way_point_dict_1_3 = {}
        # 护卫舰坐标 latitude = '18.9800107513423', longitude = '124.73857522441'
        # latitude='19.071766057291', longitude='124.31824470059'
        #latitude='18.7290219073613', longitude='124.619478848439'
        # latitude='18.7715637969444', longitude='125.056196019971'
        for k, v in target_1.items():
            strkmssn_1.assign_unit_as_target(k)
            way_point_dict_1_1['latitude'] = str(v.dLatitude+0.1)
            way_point_dict_1_1['longitude'] = str(v.dLongitude-0.4)
            way_point_list_1.append(way_point_dict_1_1)
            way_point_dict_1_2['latitude'] = str(v.dLatitude-0.26)
            way_point_dict_1_2['longitude'] = str(v.dLongitude-0.1)
            way_point_list_1.append(way_point_dict_1_2)
            way_point_dict_1_3['latitude'] = str(v.dLatitude-0.2)
            way_point_dict_1_3['longitude'] = str(v.dLongitude+0.3)
            way_point_list_1.append(way_point_dict_1_3)
        strkmssn_1.assign_units(airs_1)
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike2'}.__len__() == 0:
            strkmssn_2 = side.add_mission_strike('strike2', 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_2.set_flight_size_check('false')
        else:
            return False
        way_point_list_2 = []
        way_point_dict_2_1 = {}
        way_point_dict_2_2 = {}
        way_point_dict_2_3 = {}
        # 驱逐舰坐标latitude='19.7853375229384', longitude='124.955187168239'
        # latitude = '20.1693014453594', longitude = '124.765683212817'
        # latitude='20.0840265139753', longitude='125.260454871215'
        # latitude='19.5769601950725', longitude='125.357664592322'
        for k, v in target_1.items():
            strkmssn_2.assign_unit_as_target(k)
            way_point_dict_2_1['latitude'] = str(v.dLatitude+0.4)
            way_point_dict_2_1['longitude'] = str(v.dLongitude-0.2)
            way_point_list_2.append(way_point_dict_2_1)
            way_point_dict_2_2['latitude'] = str(v.dLatitude + 0.3)
            way_point_dict_2_2['longitude'] = str(v.dLongitude+0.32)
            way_point_list_2.append(way_point_dict_2_2)
            way_point_dict_2_3['latitude'] = str(v.dLatitude - 0.2)
            way_point_dict_2_3['longitude'] = str(v.dLongitude + 0.4)
            way_point_list_2.append(way_point_dict_2_3)
        strkmssn_2.assign_units(airs_2)
        # 通过 ctrl +x 拿到航线设置的点
        side.add_plan_way(0, 'strike1Way')
        side.add_plan_way(0, 'strike2Way')
        # wayPointList1 = [{'latitude': '26.0979297169117', 'longitude': '153.365146994643'},
        #                  {'latitude': '26.3202842588887', 'longitude': '156.042461903776'},
        #                  {'latitude': '26.1944400170521', 'longitude': '158.022842478336'}]
        # wayPointList1 = [{'latitude': '19.1808952372184', 'longitude': '124.50691441902'},
        #                  {'latitude': '19.0169433871823', 'longitude': '124.766789559568'},
        #                  {'latitude': '18.901098539356', 'longitude': '125.17569226695'}]
        # 试试这组点
        wayPointList1 = [{'latitude': '19.1906288776611', 'longitude': '124.498276037883'},
                         {'latitude': '19.0040045706188', 'longitude': '124.75204797737'},
                         {'latitude': '18.89443252942', 'longitude': '125.164759078979'}]
        # wayPointList2 = [{'latitude': '20.8369806011166', 'longitude': '125.367202439529'},
        #                  {'latitude': '20.4787088059178', 'longitude': '126.106675816174'},
        #                  {'latitude': '20.0353095192728', 'longitude': '126.191906273703'}]
        # latitude = '20.0757866251387', longitude = '124.348583728704'
        # latitude = '19.8203833788561', longitude = '124.844006741679'
        # latitude = '19.3408129429909', longitude = '125.055033853143'
        # 试试这组点
        wayPointList2 = [{'latitude': '20.0757866251387', 'longitude': '124.348583728704'},
                         {'latitude': '19.8203833788561', 'longitude': '124.844006741679'},
                         {'latitude': '19.3408129429909', 'longitude': '125.055033853143'}]
        # for item in wayPointList2:
        #     side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        if len(way_point_list_1) != 0:
            for item in way_point_list_1:
                side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])
        else:
            for item in wayPointList2:
                side.add_plan_way_point('strike1Way', item['longitude'], item['latitude'])

        strkmssn_1.add_plan_way_to_mission(0, 'strike1Way')

        # wayPointList2 = [{'latitude': '25.2543871879078', 'longitude': '153.238096612711'},
        #                  # {'latitude': '22.1273995718291', 'longitude': '156.353268774315'},
        #                  {'latitude': '25.0437456203838', 'longitude': '156.012005422884'},
        #                  {'latitude': '25.3555661789075', 'longitude': '157.515723257979'}]
        # wayPointList2 = [{'latitude': '19.7548029997645', 'longitude': '124.900855835351'},
        #                  {'latitude': '19.7870155130159', 'longitude': '125.376033225851'},
        #                  {'latitude': '19.4354255172288', 'longitude': '125.673091491897'}]
        # latitude = '20.8369806011166', longitude = '125.367202439529'
        # latitude = '20.4787088059178', longitude = '126.106675816174'
        # latitude = '20.0353095192728', longitude = '126.191906273703'

        # for item in wayPointList1:
        #     side.add_plan_way_point('strike2Way', item['longitude'], item['latitude'])
        if len(way_point_list_2) != 0:
            print('+++++++++++++')
            for item in way_point_list_2:
                side.add_plan_way_point('strike2Way', item['longitude'], item['latitude'])
        else:
            for item in wayPointList1:
                side.add_plan_way_point('strike2Way', item['longitude'], item['latitude'])
        strkmssn_2.add_plan_way_to_mission(0, 'strike2Way')
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
                edit_thort_doctrine(patrol_mission)
                # doctrine_xl2 = patrol_mission.get_doctrine()
                # edit_weapon_doctrine(doctrine=doctrine_xl2)

    airs_dic = side.aircrafts
    # v is activeunit.py 中 class CActiveUnit 中的属性:
    airsOnMssn = {k: v for k, v in airs_dic.items() if v.strActiveUnitStatus.find('正在执行任务') > 0}
    # 获取在空飞机
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 9}
    contacts = side.contacts
    if airsOnMssn.__len__() == 0:
        return False
    if len(contacts) == 0 or len(airs) == 0:
        return False

    mssnSitu = side.strikemssns
    strkmssn = [v for v in mssnSitu.values() if 'strike' in v.strName]
    if len(strkmssn) != 2:
        return False
    # 'strike1'和61行，70行的'strike1'、'strike2'对应
    strkmssn_1 = [v for v in mssnSitu.values() if v.strName == 'strike1'][0]
    strkmssn_2 = [v for v in mssnSitu.values() if v.strName == 'strike2'][0]
    # 设置任务条令
    doctrine = strkmssn_1.get_doctrine()
    # doctrine.set_emcon_according_to_superiors('false')
    # 3：是, 编组成员达到器状态武时离开编队返回基地
    if doctrine.m_WeaponStateRTB != 3:
        doctrine.set_weapon_state_for_air_group('3')  # m_WeaponStateRTB
    if doctrine.m_GunStrafeGroundTargets != 1:
        doctrine.gun_strafe_for_aircraft('1')  # m_GunStrafeGroundTargets
    if doctrine.m_BingoJokerRTB != 0:
        doctrine.set_fuel_state_for_air_group('3')  # m_BingoJokerRTB
        # 0， 对海目标自由开火
    if doctrine.m_WCS_Surface != 0:
        doctrine.set_weapon_control_status('weapon_control_status_surface', '0')
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
        doctrine_2.set_fuel_state_for_air_group('3')  # m_BingoJokerRTB
    if doctrine_2.m_WCS_Surface != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_surface', '0')
    if doctrine_2.m_WCS_Air != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_air', '0')
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions_2 = [v for v in patrol_missions_dic.values() if v.strName == side_name + 'xl' + '2'][0]
    patrol_doctrine_2 = patrol_missions_2.get_doctrine()
    patrol_doctrine_2.gun_strafe_for_aircraft('1')
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
            patrol_mission.set_flight_size(1)
            patrol_mission.set_opa_check('true')
            patrol_mission.set_wwr_check('true')
            patrol_mission.set_emcon_usage('false')
            # patrol_mission.set_throttle_transit('Cruise')
            edit_thort_doctrine(patrol_mission)

            # 如果任务没有设置航线，就添加航线
            for air in airs_xl1.values():
                if air:
                    # print('air1',air.strName)
                    # air.get_valid_weapon_load()
                    # 如果飞机的纬度在rp2点纬度上下0.15的范围或者飞机的经度和船的经度相差0.5，就continue，跳过设置航线。
                    # if (xl1_lat - 0.15) < air.dLatitude < (xl1_lat + 0.15) or air.dLongitude > ship_1.dLongitude + 0.3:
                    if '返回基地' in air.strActiveUnitStatus:
                        continue
                    # 航路点设置
                    # air.plot_course([(xl2_lat, xl2_lon)])
                    if air.strName == 'EC-130H #2':
                        doctrine = air.get_doctrine()
                        doctrine.set_em_control_status('OECM', 'Active')
                        air.plot_course([(xl1_lat-0.04, xl1_lon-0.9)])
    # update_patrol_zone(side_name, scenario)
    # latitude = '22.7570878953045', longitude = '116.499626760716' 异常点
    # latitude = '21.7577196762901', longitude = '122.64076180346'
    return False


# 躲避驱逐舰接口,暂时没有用
def evade_ship(geopoint_target, air, mission_doctrine):
    geopoint_air = (air.dLatitude, air.dLongitude)
    if geopoint_target:
        dis = get_horizontal_distance(geopoint_air, geopoint_target)
        if dis <= 60:
            mission_doctrine.ignore_plotted_course('yes')
            genpoint_away = get_end_point(geopoint_air, 15, (air.fCurrentHeading + 150))
            air.plot_course([genpoint_away])


# 创建巡逻任务
def create_patrol_mission(side_name, scenario):
    print('开始创建巡逻任务')
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
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
    # point_1 = [(21.8210656716398,122.356667127581),(21.8752434450009,122.768058783733),(21.5245647261449,122.005001630342),(21.6236431494821,123.354562698353)]
    point_1 = [(21.8210656716398, 122.356667127581), (21.8752434450009, 122.768058783733),
               (21.6701551543473, 122.35337044599), (21.6698815188537, 122.741326377829)]
    '''
    这四个点是手动设置的巡逻区，小范围,名字是RP-3756,RP-3760,RP-3761,RP-3762,先试试这四个点
    latitude = '21.8210656716398', longitude = '122.356667127581'
    latitude = '21.8752434450009', longitude = '122.768058783733'
    latitude = '21.5245647261449', longitude = '122.005001630342'
    latitude = '21.6236431494821', longitude = '123.354562698353'
    '''

    # lat: 纬度， lon：经度
    # xl1
    rp1 = side.add_reference_point(side_name + 'rp1', point_1[0][0], point_1[0][1])
    rp2 = side.add_reference_point(side_name + 'rp2', point_1[1][0], point_1[1][1])
    rp3 = side.add_reference_point(side_name + 'rp3', point_1[2][0], point_1[2][1])
    rp4 = side.add_reference_point(side_name + 'rp4', point_1[3][0], point_1[3][1])
    point_list.append([rp1, rp2, rp3, rp4])
    '''
    airs = side.aircrafts
    for k, v in airs.items():
        if v.strName == 'EC-130H #1':
            lat, lon = v.dLatitude, v.dLongitude
            rp9 = side.add_reference_point(side_name + 'rp9', lat, lon)
            rp10 = side.add_reference_point(side_name + 'rp10', lat + 0.2, lon + 0.3)
            rp11 = side.add_reference_point(side_name + 'rp11', lat - 0.25, lon - 0.25)
            rp12 = side.add_reference_point(side_name + 'rp12', lat - 0.3, lon + 0.3)
            point_list.append([rp9, rp10, rp11, rp12])
            break
        elif v.strName == 'EC-130H #2':
            lat, lon = v.dLatitude, v.dLongitude
            rp9 = side.add_reference_point(side_name + 'rp9', lat, lon)
            rp10 = side.add_reference_point(side_name + 'rp10', lat + 0.1, lon + 0.1)
            rp11 = side.add_reference_point(side_name + 'rp11', lat - 0.15, lon - 0.15)
            rp12 = side.add_reference_point(side_name + 'rp12', lat - 0.2, lon + 0.2)
            point_list.append([rp9, rp10, rp11, rp12])
            break
    '''
    return point_list

# 另写一个创建巡逻区，这次把两个巡逻任务分开执行，试试效果
def create_patrol_zone_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # point_1 = [(22.181378549063, 121.049571002033), (22.1691773335694, 124.194508316028),
    #            (20.6722068167905, 121.062131270682), (20.6370176672735, 124.156690488837)]
    point_1 = [(21.8210656716398,122.356667127581),(21.8752434450009,122.768058783733),(21.5245647261449,122.005001630342),(21.6236431494821,123.354562698353)]
    '''
    这四个点是手动设置的巡逻区，小范围,名字是RP-3756,RP-3760,RP-3761,RP-3762,先试试这四个点
    latitude = '21.8210656716398', longitude = '122.356667127581'
    latitude = '21.8752434450009', longitude = '122.768058783733'
    latitude = '21.5245647261449', longitude = '122.005001630342'
    latitude = '21.6236431494821', longitude = '123.354562698353'
    '''

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
    point_1 = [(22.1593596923231,121.147008976371), (22.5329177785997,123.746663413981), (21.2291643151066,121.162975576448), (21.705618145078,123.70585754102)]
    rp5 = side.add_reference_point(side_name + 'rp5', point_1[0][0], point_1[0][1])
    rp6 = side.add_reference_point(side_name + 'rp6', point_1[1][0], point_1[1][1])
    rp7 = side.add_reference_point(side_name + 'rp7', point_1[2][0], point_1[2][1])
    rp8 = side.add_reference_point(side_name + 'rp8', point_1[3][0], point_1[3][1])
    point_list.append([rp5, rp6, rp7, rp8])
    return point_list

# 用于巡逻任务中编辑武器条令,
def edit_weapon_doctrine(doctrine):
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
# 设置巡逻任务的油门、巡航的条例
def edit_thort_doctrine(patrol_mission):
    patrol_mission.set_throttle_transit('Cruise')
    patrol_mission.set_throttle_station('Cruise')
    patrol_mission.set_throttle_attack('Cruise')
    patrol_mission.set_transit_altitude(13000.0)
    patrol_mission.set_station_altitude(13000.0)

def update_patrol_zone(side_name, scenario):
    # 暂时没有用到
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    point_1 = [(21.3393208707725, 123.455654519338), (19.8005959781429, 122.481969737532),
               (19.128692115499, 122.815487295963), (20.7296179415939, 124.75271117856)]
    # 根据本方航空母舰的位置创建巡逻区xl1，xl2
    for k, v in airs.items():
        # lat: 纬度， lon：经度
        if 'EC-130H #1' in v.strName:
            lat, lon = v.dLatitude, v.dLongitude
            # xl1
            side.set_reference_point(side_name + 'rp9', lat, lon)
            side.set_reference_point(side_name + 'rp10', lat + 0.2, lon + 0.3)
            side.set_reference_point(side_name + 'rp11', lat - 0.25, lon - 0.25)
            side.set_reference_point(side_name + 'rp12', lat - 0.3, lon + 0.3)
        elif 'EC-130H #2' in v.strName:
            lat, lon = v.dLatitude, v.dLongitude
            side.set_reference_point(side_name + 'rp9', lat, lon)
            side.set_reference_point(side_name + 'rp10', lat + 0.2, lon + 0.3)
            side.set_reference_point(side_name + 'rp11', lat - 0.25, lon - 0.25)
            side.set_reference_point(side_name + 'rp12', lat - 0.3, lon + 0.3)



