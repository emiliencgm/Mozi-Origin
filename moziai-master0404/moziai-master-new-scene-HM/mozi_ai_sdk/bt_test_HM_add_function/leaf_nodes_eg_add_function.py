

def create_antisurfaceship_mission_add_function(side_name, scenario, task_data):
    if task_data.get('type') == 'air_attack':
        new_air_name = task_data.get('unit_name')
        new_target = task_data.get('target')
        create_new_strike_mission(side_name, scenario, new_air_name, new_target)

# 创建巡逻任务
def create_patrol_mission(side_name, scenario, task_data):
    if task_data['type'] == "patrol":
        print('new_patrol')
        new_air_name = task_data.get('unit_name')
        new_patrol_point = task_data.get('point')
        create_new_patrol_mission(side_name, scenario, new_air_name, new_patrol_point)
    return False

# 巡逻区域经纬度的生成

# 根据接收到信号，执行从外部传过来的指令
def create_new_patrol_mission(side_name, scenario, new_air_name, new_patrol_point):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs = {k: v for k, v in airs_dic.items() if v.strName in new_air_name}
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}从外部接收新的巡逻任务已创建')
    if flag != 'Yes':
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
        patrolmssn.set_start_time('2022-10-8 13:05:00')
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
    if flag != 'Yes':
        strkmssn_1 = side.add_mission_strike(strike_name, 2)
        print('创建新打船命令')
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
        strkmssn_1.set_start_time('2022-10-8 14:00:00')
        scenario.mozi_server.set_key_value(f'{side_name}从外部接收新的对舰任务已创建', 'Yes')

# 根据接收到信号，执行从外部传过来的指令,创建新的船打船任务
def create_antisurfaceship_ship_mission_add_function(side_name, scenario, task_data):
    if task_data.get('type') == 'ship_attack':
        new_ship_name = task_data.get('unit_name')
        new_target = task_data.get('target')
        create_new_strike_ship_mission(side_name, scenario, new_ship_name, new_target)

def create_new_strike_ship_mission(side_name, scenario, new_ship_name, new_target):
    side = scenario.get_side_by_name(side_name)
    ships_dic = side.ships
    ships_dic_one = {k: v for k, v in ships_dic.items() for ship_name in new_ship_name if ship_name in v.strName}
    contacts = side.contacts
    print('contacts============', contacts)
    targets = {k: v for k, v in contacts.items() for ship_name in new_target if ship_name in v.strName}
    print('targets=', targets)
    flag = scenario.mozi_server.get_value_by_key(f'{side_name}从外部接收新的舰对舰任务已创建')
    strike_name = side_name + 'new_strike_for_CG' + str(1)
    if len(targets) != 0:
        if flag != 'Yes':
            strkmssn_1 = side.add_mission_strike(strike_name, 2)
            print('创建新船打船命令')
            strkmssn_1.set_one_third_rule('false')
            strkmssn_1.set_flight_size(1)
            strkmssn_1.set_flight_size_check('false')
            # targets = {k: v for k, v in contacts.items() for ship_name in new_target if ship_name in v.strName}
            # print('targets=', targets)
            for k, v in targets.items():
                # set_mark_contact设置目标对抗关系,H is 敌方
                side.set_mark_contact(k, 'H')
            for k, v in targets.items():
                strkmssn_1.assign_unit_as_target(k)
            strkmssn_1.assign_units(ships_dic_one)
            strike_plot_name = 'new_strikeway_CG'
            # latitude = '26.3042164818373', longitude = '126.348698937408'
            # latitude = '26.5400556639504', longitude = '126.13904462382'
            # latitude = '26.7660759251427', longitude = '125.960240197087'

            strike_plot_point_list = [{'latitude': 26.3042164818373, 'longitude': 126.348698937408},
                         {'latitude': 26.5400556639504, 'longitude': 126.13904462382},
                         {'latitude': 26.7660759251427, 'longitude': 125.960240197087}]
            side.add_plan_way(0, strike_plot_name)
            for item in strike_plot_point_list:
                side.add_plan_way_point(strike_plot_name, item['longitude'], item['latitude'])
            strkmssn_1.add_plan_way_to_mission(0, strike_plot_name)
            # strkmssn_1.set_start_time('2022-10-8 14:00:00')
            scenario.mozi_server.set_key_value(f'{side_name}从外部接收新的舰对舰任务已创建', 'Yes')