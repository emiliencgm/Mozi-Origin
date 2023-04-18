import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission

# 反舰
anti_ship_air_dict = {"1#": ["F-16A #1", "F-16A #2", "F-16A #3", "F-16A #4", "F-16A #5", "F-16A #6"],
                      "2#": ["F-16A #01", "F-16A #02", "F-16A #03", "F-16A #04", "F-16A #05", "F-16A #06"]}
# 战斗机
fighter_dict = {"1#": ["F-16A #7", "F-16A #8",
                       "F-16A #9"], "2#": ["F-16A #07", "F-16A #08", "F-16A #09"]}
# 预警机
warning_air = "E-2K #1"
# 电子战飞机
jammer_dict = {"1#": "EC-130H #1", "2#": "EC-130H #2"}


# 创建预警机巡逻任务
def create_patrol_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    # 如果预警机被打掉，则返回false
    airs_c = [v for v in airs_dic.values() if v.strName == warning_air]
    if len(airs_c) == 0:
        return False
    # 获取mission任务
    patrol_missions_dic = side.get_patrol_missions()
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}巡逻任务已创建')
    if flag == 'Yes':
        return False
    doctrine = side.get_doctrine()
    doctrine.set_em_control_status('Radar', 'Active')
    doctrine.set_em_control_status('Sonar', 'Active')
    doctrine.set_em_control_status('OECM', 'Active')

    patrol_mission_name = [
        mission.strName for mission in patrol_missions_dic.values()]
    # 根据巡逻区参考点，创建巡逻区
    point_list, _ = create_warn_air_points(side_name, scenario)
    i = 1

    point_str = []
    for name in point_list:
        point_str.append(name.strName)
    # 新建巡逻区名字xl1
    patrol_name = side_name + 'xl' + str(i)

    # 创建巡逻任务，设置1/3规则
    patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str)
    # patrolmssn.set_one_third_rule('true')
    patrolmssn.set_one_third_rule('false')

    scenario.mozi_server.set_key_value(f'{side_name}巡逻任务已创建', 'Yes')
    return False


# 创建预警机巡逻区和警戒区
def create_warn_air_points(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    # 巡逻区
    points_list = [[21.1711616780749, 120.68559255139], [21.3711600018991, 121.620654729637], [
        20.8449476414427, 121.691220246622], [20.6620369217392, 120.847397397822]]
    rp_list = []
    for i in range(4):
        rpi = side.add_reference_point(
            side_name + 'rp'+str(i), points_list[i][0], points_list[i][1])
        rp_list.append(rpi)

    # 警戒区
    points_list_1 = [[21.2528547657298, 120.578918475062], [21.5686327477297, 121.691315873898], [
        20.7298024102888, 121.814263868626], [20.5132012869007, 120.707490111922]]
    rp_warn_list = []
    for i in range(4):
        rpi = side.add_reference_point(
            side_name + 'rp'+str(i), points_list_1[i][0], points_list_1[i][1])
        rp_warn_list.append(rpi)
    return rp_list, rp_warn_list


# 更新巡逻任务,让预警机到达指定位置，打开雷达
def update_patrol_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    # 任务名称
    patrol_name = side_name + "xl1"
    airs_dic = side.aircrafts

    # 执行任务的飞机,
    airs = {k: v for k, v in airs_dic.items() if v.strName == warning_air}
    for i in airs:
        # 设置雷达和干扰
        doctrine2 = airs[i].get_doctrine()
        doctrine2.set_emcon_according_to_superiors('no')
        airs[i].set_radar_shutdown('false')
        # airs[i].set_radar_shutdown('true')
        airs[i].set_oecm_shutdown('false')
        # airs[i].set_oecm_shutdown('true')
        airs[i].set_sonar_shutdown('false')
        # airs[i].set_sonar_shutdown('true')
    # 获取巡逻任务，如果巡逻任务为0，说明还没有创建巡逻任务。
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    if len(patrol_missions) == 0:
        return False
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == patrol_name:
            # 获取推演方条令
            doctrine_xl1 = patrol_mission.get_doctrine()
            # 设置单架飞机的武器状态,2002可使用航炮
            doctrine_xl1.set_weapon_state_for_aircraft(2002)
            # 分配单元
            patrol_mission.assign_units(airs)
            # 设置任务编队规模
            patrol_mission.set_flight_size(1)

            _, warn_area = create_warn_air_points(side_name, scenario)
            patrol_mission.set_prosecution_zone(warn_area)
    print("巡逻成功")
    return False


# # 创建对海打击任务
# def create_att_ship(side_name, scenario):
#     side = scenario.get_side_by_name(side_name)
#     airs_dic = side.aircrafts

#     # 如果已有任务,返回false
#     # side.get_strike_missions()
#     flag = scenario.mozi_server.get_value_by_key(f'{side_name}打击任务已创建')
#     if flag == 'Yes':
#         return False
#     # 第一编队(护航与打击)
#     patrolmssn_1 = side.add_mission_strike("对海打击1", 2)
#     patrolmssn_1.set_one_third_rule('false')

#     patrolmssn_2 = side.add_mission_strike("对海打击2", 2)
#     patrolmssn_2.set_one_third_rule("false")
#     scenario.mozi_server.set_key_value(f'{side_name}打击任务已创建', 'Yes')

#     return False


# # 更新对海打击任务
# def update_att_ship(side_name, scenario):
#     side = scenario.get_side_by_name(side_name)
#     airs_dic = side.aircrafts
#     # strike_mission_dic = side.get_strike_missions()

#     stricke_name = ["对海打击1", "对海打击2"]
#     airs = {k: v for k, v in airs_dic.items() if v.strName != warning_air}
#     # 打开雷达和干扰
#     for i in airs:
#         doctrine2 = airs[i].get_doctrine()
#         doctrine2.set_emcon_according_to_superiors('no')
#         # airs[i].set_radar_shutdown('false')
#         airs[i].set_radar_shutdown('true')
#         # airs[i].set_oecm_shutdown('false')
#         airs[i].set_oecm_shutdown('true')
#         # airs[i].set_sonar_shutdown('false')
#         airs[i].set_sonar_shutdown('true')
#     # 任务1反舰与支援的飞机
#     att_ship_1 = {k: v for k, v in airs_dic.items(
#     ) if v.strName in anti_ship_air_dict["1#"]}
#     zy_1 = {k: v for k, v in airs_dic.items(
#     ) if v.strName in fighter_dict["1#"] or v.strName == jammer_dict["1#"]}

#     # 任务2的反舰与支援飞机
#     att_ship_2 = {k: v for k, v in airs_dic.items(
#     ) if v.strName in anti_ship_air_dict["2#"]}
#     zy_2 = {k: v for k, v in airs_dic.items(
#     ) if v.strName in fighter_dict["2#"] or v.strName == jammer_dict["2#"]}

#     # 判断对海打击是否创建
#     strike_missions_dic = side.get_strike_missions()
#     strike_missions = [mission for mission in strike_missions_dic.values()]
#     if len(strike_missions) == 0:
#         return False

#     create_line(side_name, scenario)
#     for strike_mission in strike_missions:
#         if strike_mission.strName == stricke_name[0]:
#             doctrine_1 = strike_mission.get_doctrine()
#             doctrine_1.set_weapon_state_for_aircraft(2002)
#             # strike_mission.assign_units(att_ship_1)
#             for i in att_ship_1:
#                 strike_mission.assign_unit(i)
#             strike_mission.set_flight_size(1)
#             # 打击触发条件
#             strike_mission.set_minimum_trigger(1)
#             # 护航最大响应距离
#             strike_mission.set_strike_escort_response_radius(100)
#             # 设置出航航线
#             # side.add_plan_way(0, '单元航线-新')
#             strike_mission.add_plan_way_to_mission(0, 'strike1Way')
#             # 设置护航飞机
#             for i in zy_1:
#                 strike_mission.assign_unit(i, True)
#             # 起飞设置
#             strike_mission.set_strike_escort_flight_size_shooter(1)
#             strike_mission.set_flight_size_check('false')
#             pass
#         elif strike_mission.strName == stricke_name[1]:
#             doctrine_2 = strike_mission.get_doctrine()
#             doctrine_2.set_weapon_state_for_aircraft(2002)
#             # strike_mission.assign_units(att_ship_2)
#             for i in att_ship_2:
#                 strike_mission.assign_unit(i)
#             strike_mission.set_flight_size(1)
#             # 打击触发条件
#             strike_mission.set_minimum_trigger(1)
#             # 护航最大响应距离
#             strike_mission.set_strike_escort_response_radius(100)
#             # 设置出航航线
#             # side.add_plan_way(0, '单元航线-新')
#             strike_mission.add_plan_way_to_mission(0, 'strike2Way')
#             # 设置护航飞机
#             for i in zy_2:
#                 strike_mission.assign_unit(i, True)
#             # 起飞设置
#             strike_mission.set_strike_escort_flight_size_shooter(2)
#             strike_mission.set_flight_size_check('false')
#             pass
#     print("对海打击成功了")
#     return False


# 设置航线
def create_line(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    side.add_plan_way(0, 'strike1Way')
    wayPointList1 = [
        {"latitude": '20.121691366733', "longitude": '121.056323010951'},
        {'latitude': '19.0108831830151', 'longitude': '121.557533627416'},
        {'latitude': '18.3216791280064', 'longitude': '122.638665256194'},
        {'latitude': '18.2143032537401', 'longitude': '123.611727850128'},
        # {'latitude': '18.5758170644927', 'longitude': '124.370528026812'}
        # {'latitude': '18.3833960943984', 'longitude': '124.016232385939'}
        {'latitude': '18.3692284357477', 'longitude': '124.472098909489'},
        {'latitude': '18.4613435585431', 'longitude': '125.202421528917'},
        {'latitude': '18.837528450414', 'longitude': '125.875480522491'},
        {'latitude': '20.0847154610314', 'longitude': '126.051082173842'}
    ]
    for item in wayPointList1:
        side.add_plan_way_point(
            'strike1Way', item['longitude'], item['latitude'])

    side.add_plan_way(0, 'strike2Way')
    wayPointList2 = [{"latitude": '21.9829589660924', "longitude": '123.73673707386'},
                     {'latitude': '21.4583049385196',
                         'longitude': '125.161260139356'},
                     {'latitude': '20.5376405464277',
                         "longitude": '125.875697851564'},
                     {'latitude': '20.0847154610314', 'longitude': '126.051082173842'}]
    for item in wayPointList2:
        side.add_plan_way_point(
            'strike2Way', item['longitude'], item['latitude'])

    return


# 创建反舰任务
def create_att_ship(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    contacts = side.contacts
    airs_dic = side.aircrafts
    # 获取反舰任务飞机
    #
    airs_1 = {k: v for k, v in airs_dic.items(
    ) if v.strName in anti_ship_air_dict["1#"]}
    #
    airs_2 = {k: v for k, v in airs_dic.items(
    ) if v.strName in anti_ship_air_dict["2#"]}
    if len(contacts) == 0 or len(airs_1) + len(airs_2) == 0:
        return False
    # 等巡逻的飞机全部起飞后，打击任务创建，然后开始起飞
    airs_patrol = side.patrolmssns
    if not airs_patrol:
        return False

    targets = {k: v for k, v in contacts.items() if (
        ('驱逐舰' in v.strName) | ('护卫舰' in v.strName) | ('航空母舰' in v.strName))}
    target_1 = {k: v for k, v in contacts.items() if ('航空母舰' in v.strName)}
    target_2 = {k: v for k, v in contacts.items() if ('航空母舰' not in v.strName)}
    for k, v in targets.items():
        side.set_mark_contact(k, 'H')
    mssnSitu = side.strikemssns
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
        strkmssn_1 = side.add_mission_strike('strike1', 2)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_1.set_flight_size_check('false')
    else:
        return False
    for k, v in target_1.items():
        strkmssn_1.assign_unit_as_target(k)
    strkmssn_1.assign_units(airs_1)
    zy_1 = {k: v for k, v in airs_dic.items(
    ) if v.strName in fighter_dict["1#"] or v.strName == jammer_dict["1#"]}
    for i in zy_1:
        strkmssn_1.assign_unit(i, True)
        # doctrine2 = zy_1[i].get_doctrine()
        # doctrine2.set_emcon_according_to_superiors('no', "true")
        # # airs[i].set_radar_shutdown('false')
        # zy_1[i].set_radar_shutdown('true')
        # # airs[i].set_oecm_shutdown('false')
        # zy_1[i].set_oecm_shutdown('true')
        # # airs[i].set_sonar_shutdown('false')
        # zy_1[i].set_sonar_shutdown('true')
    strkmssn_1.set_strike_escort_flight_size_shooter(1)
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike2'}.__len__() == 0:
        strkmssn_2 = side.add_mission_strike('strike2', 2)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_2.set_flight_size_check('false')
    else:
        return False
    for k, v in target_2.items():
        strkmssn_2.assign_unit_as_target(k)
    zy_2 = {k: v for k, v in airs_dic.items(
    ) if v.strName in fighter_dict["2#"] or v.strName == jammer_dict["2#"]}
    for i in zy_2:
        strkmssn_2.assign_unit(i, True)
        # doctrine2 = zy_2[i].get_doctrine()
        # doctrine2.set_emcon_according_to_superiors('no', "true")
        # # airs[i].set_radar_shutdown('false')
        # zy_2[i].set_radar_shutdown('true')
        # # airs[i].set_oecm_shutdown('false')
        # zy_2[i].set_oecm_shutdown('true')
        # # airs[i].set_sonar_shutdown('false')
        # zy_2[i].set_sonar_shutdown('true')
    strkmssn_2.set_strike_escort_flight_size_shooter(1)
    strkmssn_2.assign_units(airs_2)

    # 出航路径
    create_line(side_name, scenario)
    strkmssn_1.add_plan_way_to_mission(0, 'strike1Way')
    strkmssn_2.add_plan_way_to_mission(0, 'strike2Way')
    return False


def update_att_ship(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airsOnMssn = {k: v for k, v in airs_dic.items(
    ) if v.strActiveUnitStatus.find('正在执行任务') > 0}
    airs = {k: v for k, v in airs_dic.items(
    ) if v.strName in anti_ship_air_dict["1#"] or v.strName in anti_ship_air_dict["2#"]}
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
        doctrine.set_weapon_control_status(
            'weapon_control_status_subsurface', '0')
        # 0， 对海目标自由开火
    if doctrine.m_WCS_Surface != 0:
        doctrine.set_weapon_control_status(
            'weapon_control_status_surface', '0')
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
        doctrine_2.set_weapon_control_status(
            'weapon_control_status_surface', '0')
    if doctrine_2.m_WCS_Land != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_land', '0')
    if doctrine_2.m_WCS_Air != 0:
        doctrine_2.set_weapon_control_status('weapon_control_status_air', '0')

    mssnSitu = side.strikemssns
    patrolmssn = side.patrolmssns
    target = {k: v for k, v in contacts.items() if ('DDG' in v.strName)}

    strkmssn = [v for v in mssnSitu.values() if v.strName == 'strike2'][0]
    strkPatrol = [v for v in patrolmssn.values() if v.strName ==
                  'strikePatrol']

    # 获取任务执行单元
    missionUnits = strkmssn.m_AssignedUnits.split('@')
    create = False
    for unitGuid in missionUnits:
        retreat, retreatPos = utils.check_unit_retreat_and_compute_retreat_pos(
            side, unitGuid)
        if retreat == True:
            if len(strkPatrol) == 0 & create is False:
                pos = {'latitude': list(target.values())[0].dLatitude, 'longitude': list(
                    target.values())[0].dLongitude}
                point_list = utils.create_patrol_zone(side, pos)
                postr = []
                for point in point_list:
                    postr.append(point.strName)
                strikePatrolmssn = side.add_mission_patrol(
                    'strikePatrol', 1, postr)
                # 取消满足编队规模才能起飞的限制（任务条令）
                strikePatrolmssn.set_flight_size_check('false')
                utils.change_unit_mission(
                    side, strkmssn, strikePatrolmssn, missionUnits)
                return False
            else:
                break
    return False
