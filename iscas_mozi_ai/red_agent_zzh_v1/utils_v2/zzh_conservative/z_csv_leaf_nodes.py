import random

warning_team_1 = {"卡-29 #7", "卡-29 #8"}  # left wing warning
warning_team_2 = {"卡-29 #9", "卡-29 #10"}  # right wing warning

air_defense_team_1 = {"米格-29 #1", "米格-29 #2", "米格-29 #3", "米格-29 #4", "米格-29 #5", "米格-29 #6"}  # left wing air_defense
air_defense_team_2 = {"米格-29 #7", "米格-29 #8"}  # right wing air_defense
air_defense_team_3 = {"米格-29 #9", "米格-29 #10"}  # CV base air_defense

enemy_facility = {"1号机场", "2号机场", "白云III型USA 160 P/L 2海洋监控卫星"}  # not aircraft
# 20.10, 124.5
warning_team_1_rp = [[19.52, 123.42], [20.15, 125.0], [19.20, 125.55], [18.34, 125.37]]  # 0-3
# 必须是float，int会创建失败（关键是不会提示啊，服了）
warning_team_2_rp = [[19.52, 123.42], [18.34, 125.37], [17.57, 124.27], [18.25, 123.33]]  # 4-7

air_defense_team_1_patrol_rp = [[20.25, 125.19], [19.42, 124.15], [21.27, 124.40], [20.47, 123.18]]  # 8-11
air_defense_team_2_patrol_rp = [[20.47, 123.18], [21.27, 124.40], [18.46, 123.27], [19.17, 122.09]]  # 12-15
air_defense_team_1_2_prosecution_rp = [[22.48, 124.46], [21.44, 126.53], [17.43, 121.57], [19.05, 120.38], [21.51, 122.04]]  # 24-28
air_defense_team_3_patrol_rp = [[20.46, 125.09], [19.35, 126.35], [17.42, 125.05], [18.09, 123.09]]  # 16-19
air_defense_team_3_prosecution_rp = [[20.54, 126.03], [19.33, 127.19], [16.45, 124.59], [17.27, 122.51]]  # 20-23


def warning_patrol_condition(side_name, scenario):
    print("\n===>预警机巡逻任务<===")
    side = scenario.get_side_by_name(side_name)
    airs = side.aircrafts
    we_air_num = 0
    for k, v in airs.items():
        if v.strName in warning_team_1 or v.strName in warning_team_2:
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
    # print(f"目前存在{len(patrol_missions)}个预警巡逻任务")
    airs = side.aircrafts
    if len(patrol_missions) <= 0:
        return False
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + '左翼预警':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if not len(mission_units) >= 2:
                doctrine = patrol_mission.get_doctrine()
                doctrine.set_weapon_state_for_aircraft(4002)
                warning_airs = {}
                for k, v in airs.items():
                    if v.strName in warning_team_1:
                        warning_airs[k] = v
                patrol_mission.assign_units(warning_airs)
                patrol_mission.set_flight_size(1)
                for air in warning_airs.values():
                    air.set_radar_shutdown(False)
        if patrol_mission.strName == side_name + '右翼预警':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if not len(mission_units) >= 2:
                doctrine = patrol_mission.get_doctrine()
                doctrine.set_weapon_state_for_aircraft(4002)
                warning_airs = {}
                for k, v in airs.items():
                    if v.strName in warning_team_2:
                        warning_airs[k] = v
                patrol_mission.assign_units(warning_airs)
                patrol_mission.set_flight_size(1)
                for air in warning_airs.values():
                    air.set_radar_shutdown(False)
    return True


def create_warning_patrol_mission(side_name, scenario):
    print("==>创建预警机巡逻任务")
    side = scenario.get_side_by_name(side_name)
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}左翼预警巡逻任务已创建')
    # 左翼预警机预警任务
    if not flag == 'Yes':
        point_list = []
        for i in range(len(warning_team_1_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i), warning_team_1_rp[i][0],
                                             warning_team_1_rp[i][1])
            point_list.append(point)
        point_str = []
        for name in point_list:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + '左翼预警'
        # 创建巡逻任务，设置1/3规则
        patrol_mission = side.add_mission_patrol(patrol_name, 0, point_str)
        patrol_mission.set_one_third_rule('false')
        patrol_mission.set_prosecution_zone(point_str)
        scenario.mozi_server.set_key_value(f'{side_name}左翼预警巡逻任务已创建', 'Yes')

    flag = scenario.mozi_server.get_value_by_key(f'{side_name}右翼预警巡逻任务已创建')
    # 右翼预警机预警任务
    if not flag == 'Yes':
        point_list = []
        for i in range(len(warning_team_2_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i + 4), warning_team_2_rp[i][0],
                                             warning_team_2_rp[i][1])
            point_list.append(point)
        point_str = []
        for name in point_list:
            point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + '右翼预警'
        # 创建巡逻任务，设置1/3规则
        patrol_mission = side.add_mission_patrol(patrol_name, 0, point_str)
        patrol_mission.set_one_third_rule('false')
        patrol_mission.set_prosecution_zone(point_str)
        scenario.mozi_server.set_key_value(f'{side_name}右翼预警巡逻任务已创建', 'Yes')
    return True


def air_defense_condition(side_name, scenario):
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
        if v.strName in air_defense_team_1 \
                or v.strName in air_defense_team_2 \
                or v.strName in air_defense_team_3:
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


def update_air_defense_mission(side_name, scenario):
    print("==>更新防空巡逻任务")
    side = scenario.get_side_by_name(side_name)
    patrol_missions_dic = side.get_patrol_missions()
    patrol_missions = [mission for mission in patrol_missions_dic.values()]
    # print(f"目前存在{len(patrol_missions)}个防空巡逻任务")
    airs = side.aircrafts
    for patrol_mission in patrol_missions:
        if patrol_mission.strName == side_name + '左翼防空':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if not len(mission_units) >= 4:
                doctrine = patrol_mission.get_doctrine()
                doctrine.set_weapon_state_for_aircraft(2001)
                doctrine.set_fuel_state_for_air_group("YesLeaveGroup")
                air_defense_airs = {}
                for k, v in airs.items():
                    if v.strName in air_defense_team_1:
                        air_defense_airs[k] = v
                patrol_mission.assign_units(air_defense_airs)
                patrol_mission.set_flight_size(2)
                for air in air_defense_airs.values():
                    air.set_radar_shutdown(False)
        if patrol_mission.strName == side_name + '右翼防空':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if not len(mission_units) >= 4:
                doctrine = patrol_mission.get_doctrine()
                doctrine.set_weapon_state_for_aircraft(2001)
                doctrine.set_fuel_state_for_air_group("YesLeaveGroup")
                air_defense_airs = {}
                for k, v in airs.items():
                    if v.strName in air_defense_team_2:
                        air_defense_airs[k] = v
                patrol_mission.assign_units(air_defense_airs)
                patrol_mission.set_flight_size(2)
                for air in air_defense_airs.values():
                    air.set_radar_shutdown(False)
        if patrol_mission.strName == side_name + '基地防空':
            mission_units = patrol_mission.m_AssignedUnits.split('@')
            if not len(mission_units) >= 2:
                doctrine = patrol_mission.get_doctrine()
                doctrine.set_weapon_state_for_aircraft(2001)
                doctrine.set_fuel_state_for_air_group("YesLeaveGroup")
                air_defense_airs = {}
                for k, v in airs.items():
                    if v.strName in air_defense_team_3:
                        air_defense_airs[k] = v
                patrol_mission.assign_units(air_defense_airs)
                patrol_mission.set_flight_size(1)
                for air in air_defense_airs.values():
                    air.set_radar_shutdown(False)
    return False


def create_air_defense_mission(side_name, scenario):
    print("==>创建防空巡逻任务")
    side = scenario.get_side_by_name(side_name)
    # 共享警戒区
    prosecution_point_list = []
    for i in range(len(air_defense_team_1_2_prosecution_rp)):
        point = side.add_reference_point(side_name + 'rp' + str(i + 24),
                                         air_defense_team_1_2_prosecution_rp[i][0],
                                         air_defense_team_1_2_prosecution_rp[i][1])
        prosecution_point_list.append(point)
    prosecution_point_str = []
    for name in prosecution_point_list:
        prosecution_point_str.append(name.strName)
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}右翼防空巡逻任务已创建')
    if not flag == 'Yes':
        patrol_point_list = []
        for i in range(len(air_defense_team_1_patrol_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i + 8), air_defense_team_1_patrol_rp[i][0],
                                             air_defense_team_1_patrol_rp[i][1])
            patrol_point_list.append(point)
        patrol_point_str = []
        for name in patrol_point_list:
            patrol_point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + '右翼防空'
        # 创建巡逻任务，设置1/3规则
        patrol_mission = side.add_mission_patrol(patrol_name, 0, patrol_point_str)
        patrol_mission.set_one_third_rule('false')
        patrol_mission.set_prosecution_zone(prosecution_point_str)
        scenario.mozi_server.set_key_value(f'{side_name}右翼防空巡逻任务已创建', 'Yes')

    flag = scenario.mozi_server.get_value_by_key(f'{side_name}左翼防空巡逻任务已创建')
    if not flag == 'Yes':
        patrol_point_list = []
        for i in range(len(air_defense_team_2_patrol_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i + 12), air_defense_team_2_patrol_rp[i][0],
                                             air_defense_team_2_patrol_rp[i][1])
            patrol_point_list.append(point)
        patrol_point_str = []
        for name in patrol_point_list:
            patrol_point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + '左翼防空'
        # 创建巡逻任务，设置1/3规则
        patrol_mission = side.add_mission_patrol(patrol_name, 0, patrol_point_str)
        patrol_mission.set_one_third_rule('false')
        patrol_mission.set_prosecution_zone(prosecution_point_str)
        scenario.mozi_server.set_key_value(f'{side_name}左翼防空巡逻任务已创建', 'Yes')

    flag = scenario.mozi_server.get_value_by_key(f'{side_name}基地防空巡逻任务已创建')
    if not flag == 'Yes':
        patrol_point_list = []
        for i in range(len(air_defense_team_3_patrol_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i + 16), air_defense_team_3_patrol_rp[i][0],
                                             air_defense_team_3_patrol_rp[i][1])
            patrol_point_list.append(point)
        prosecution_point_list = []
        for i in range(len(air_defense_team_3_prosecution_rp)):
            point = side.add_reference_point(side_name + 'rp' + str(i + 20), air_defense_team_3_prosecution_rp[i][0],
                                             air_defense_team_3_prosecution_rp[i][1])
            prosecution_point_list.append(point)
        patrol_point_str = []
        for name in patrol_point_list:
            patrol_point_str.append(name.strName)
        prosecution_point_str = []
        for name in prosecution_point_list:
            prosecution_point_str.append(name.strName)
        # 新建巡逻区名字
        patrol_name = side_name + '基地防空'
        # 创建巡逻任务，设置1/3规则
        patrol_mission = side.add_mission_patrol(patrol_name, 0, patrol_point_str)
        patrol_mission.set_one_third_rule('false')
        patrol_mission.set_prosecution_zone(prosecution_point_str)
        scenario.mozi_server.set_key_value(f'{side_name}基地防空巡逻任务已创建', 'Yes')
    return True


def create_ship_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    ships = side.ships
    # 舰船机动，所有船前进
    # 舰船干扰开启
    for k, v in ships.items():
        v.set_radar_shutdown(False)
        v.set_oecm_shutdown(False)
        target_position = [(v.dLatitude+0.2, v.dLongitude-0.2),
                           (v.dLatitude+0.4, v.dLongitude-0.2)]
        v.plot_course(target_position)


