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
            # for point in support_point_list:
            #     point_str_support = []
            #     for name in point:
            #         point_str_support.append(name.strName)
            # supportmssn = side.add_mission_support(support_name, point_str_support)
            area_str = str(support_point_list).replace('[', '').replace(']', '')
            detail = f"{{Zone={{{area_str}}}}}"
            cmd_1 = "ReturnObj(ScenEdit_AddMission('{}','{}','{}',{}))".format(side.strGuid, support_name, 'Support', detail)
            scenario.mozi_server.throw_into_pool(cmd_1)
            add_support_message = scenario.mozi_server.send_and_recv(cmd_1)
            print('add_support_message=', add_support_message)
            print('支援任务已创建')
            # supportmssn.set_is_active('true')
            is_active = 'true'
            str_set = str(is_active).lower()
            lua = "ScenEdit_SetMission('%s','%s',{isactive='%s'})" % (side_name, support_name, str_set)
            is_active_message = scenario.mozi_server.send_and_recv(lua)
            print('is_active_message=', is_active_message)
            # supportmssn.assign_units(airs_support)
            for k, v in airs_support.items():
                cmd_2 = "ScenEdit_AssignUnitToMission('{}', '{}')".format(v.strGuid, support_name)
                scenario.mozi_server.throw_into_pool(cmd_2)
                assign_unit_message = scenario.mozi_server.send_and_recv(cmd_2)
                print('assign_unit=', assign_unit_message)

            # supportmssn.set_one_third_rule(support_rule.get('one_third_rule'))
            is_one_third = support_rule.get('one_third_rule')
            cmd_3 = 'ScenEdit_SetMission("%s","%s", {oneThirdRule=%s})' % \
                  (side_name, support_name, str(is_one_third).lower())
            scenario.mozi_server.throw_into_pool(cmd_3)
            one_third_message = scenario.mozi_server.send_and_recv(cmd_3)
            print('one_third_message=', one_third_message)
            # supportmssn.set_flight_size(support_rule.get('flight_size'))
            flight_size = support_rule.get('flight_size')
            cmd_4 = 'ScenEdit_SetMission("' + side_name + '","' + support_name + '",{flightSize=' + str(
                flight_size) + '})'
            scenario.mozi_server.throw_into_pool(cmd_4)
            flight_size_message = scenario.mozi_server.send_and_recv(cmd_4)
            print('flight_size_message=', flight_size_message)

            # supportmssn.set_flight_size_check(support_rule.get('set_flight_size_check'))
            use_flight_size_check = support_rule.get('set_flight_size_check')
            cmd_5 = 'ScenEdit_SetMission("' + side_name + '","' + support_name + '", {''useFlightSize =' + str(
                use_flight_size_check).lower() + '})'
            print('cmd_5=', cmd_5)
            scenario.mozi_server.throw_into_pool(cmd_5)
            flight_size_check_message = scenario.mozi_server.send_and_recv(cmd_5)
            print('flight_size_check_message=', flight_size_check_message)

            # supportmssn.set_start_time(start_mission_time)
            cmd_str = "ScenEdit_SetMission('" + side_name + "','" + support_name + "',{starttime='" + start_mission_time + "'})"
            support_start_time = scenario.mozi_server.send_and_recv(cmd_str)
            print('support_start_time=', support_start_time)
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
            # ps_str = []
            # for ps in prosecution_zone_list:
            #     for name in ps:
            #         ps_str.append(name.strName)
            patrol_zone = order_dic.get('patrol_zone')
            patrol_point_list = create_patrol_zone(side_name, scenario, patrol_zone, i)
            # for point in patrol_point_list:
            #     point_str_patrol = []
            #     for name in point:
            #         point_str_patrol.append(name.strName)
            # patrolmssn = side.add_mission_patrol(patrol_name, 0, point_str_patrol)
            patrol_type = 'AAW'
            area_str = str(patrol_point_list).replace('[', '').replace(']', '')
            detail = f"{{type='{patrol_type}', Zone={{{area_str}}}}}"
            cmd = "ReturnObj(ScenEdit_AddMission('{}','{}','{}',{}))".format(side.strGuid, patrol_name, 'Patrol', detail)
            scenario.mozi_server.throw_into_pool(cmd)
            add_patrol_message = scenario.mozi_server.send_and_recv(cmd)
            print('add_patrol_message=', add_patrol_message)
            print('xl任务已创建')
            # patrolmssn.set_is_active('true')
            is_active = 'true'
            str_set = str(is_active).lower()
            lua = "ScenEdit_SetMission('%s','%s',{isactive='%s'})" % (side_name, patrol_name, str_set)
            patrol_is_active_message = scenario.mozi_server.send_and_recv(lua)
            print('patrol_is_active_message=', patrol_is_active_message)
            # patrolmssn.assign_units(airs_patrol)
            for k, v in airs_patrol.items():
                cmd_2 = "ScenEdit_AssignUnitToMission('{}', '{}')".format(v.strGuid, patrol_name)
                scenario.mozi_server.throw_into_pool(cmd_2)
                patrol_assign_unit = scenario.mozi_server.send_and_recv(cmd_2)
                print('patrol_assign_unit=', patrol_assign_unit)
            # patrolmssn.set_patrol_zone(point_str_patrol)
            area_str = str(patrol_point_list).replace('[', '').replace(']', '')
            lua_script = f"ScenEdit_SetMission('{side_name}','{patrol_name}',{{patrolZone={{{area_str}}}}})"
            scenario.mozi_server.throw_into_pool(lua_script)
            patrol_zone_message = scenario.mozi_server.send_and_recv(lua_script)
            print('设置巡逻区=', patrol_zone_message)
            print('patrol_zone====', patrol_point_list)
            # patrolmssn.set_prosecution_zone(ps_str)
            area_str = str(prosecution_zone_list).replace('[', '').replace(']', '')
            lua_script = f"ScenEdit_SetMission('{side_name}','{patrol_name}',{{prosecutionZone={{{area_str}}}}})"
            scenario.mozi_server.throw_into_pool(lua_script)
            prosecution_zone_message = scenario.mozi_server.send_and_recv(lua_script)
            print("设置警戒区=", prosecution_zone_message)

            # patrolmssn.set_one_third_rule(patrol_rule.get('one_third_rule'))
            is_one_third = patrol_rule.get('one_third_rule')
            cmd_3 = 'ScenEdit_SetMission("%s","%s", {oneThirdRule=%s})' % \
                    (side_name, patrol_name, str(is_one_third).lower())
            scenario.mozi_server.throw_into_pool(cmd_3)
            scenario.mozi_server.send_and_recv(cmd_3)
            # patrolmssn.set_flight_size(patrol_rule.get('flight_size'))
            flight_size = patrol_rule.get('flight_size')
            cmd_4 = 'ScenEdit_SetMission("' + side_name + '","' + patrol_name + '",{flightSize=' + str(
                flight_size) + '})'
            scenario.mozi_server.throw_into_pool(cmd_4)
            scenario.mozi_server.send_and_recv(cmd_4)
            # patrolmssn.set_flight_size_check(patrol_rule.get('set_flight_size_check'))
            use_flight_size_check = patrol_rule.get('set_flight_size_check')
            cmd_5 = 'ScenEdit_SetMission("' + side_name + '","' + patrol_name + '", {''useFlightSize =' + str(
                use_flight_size_check).lower() + '})'
            scenario.mozi_server.throw_into_pool(cmd_5)
            scenario.mozi_server.send_and_recv(cmd_5)
            # patrolmssn.set_opa_check(patrol_rule.get('opa_check'))
            is_check_opa = patrol_rule.get('opa_check')
            cmd_6 = "ScenEdit_SetMission('" + side_name + "', '" + patrol_name + "', { checkOPA = " + is_check_opa + "})"
            scenario.mozi_server.throw_into_pool(cmd_6)
            check_opa_message = scenario.mozi_server.send_and_recv(cmd_6)
            print('check_opa_message=', check_opa_message)

            # patrolmssn.set_wwr_check(patrol_rule.get('wwr_check'))
            is_check_wwr = patrol_rule.get('wwr_check')
            cmd_7 = "ScenEdit_SetMission('" + side_name + "', '" + patrol_name \
                  + "', { checkWWR = " + str(is_check_wwr).lower() + "})"
            scenario.mozi_server.throw_into_pool(cmd_7)
            check_wwr_message = scenario.mozi_server.send_and_recv(cmd_7)
            print('check_wwr_message=', check_wwr_message)
            # patrolmssn.set_emcon_usage(patrol_rule.get('emcon_usage'))
            is_active_emcon = patrol_rule.get('emcon_usage')
            # cmd_8 = "ScenEdit_SetMission('" + str(side_name) + "', '" + str(
            #     side.strGuid) + "', { activeEMCON = " + str(is_active_emcon).lower() + "})"
            # scenario.mozi_server.throw_into_pool(cmd_8)
            # is_active_emcon_message = scenario.mozi_server.send_and_recv(cmd_8)
            # print('is_active_emcon_message=', is_active_emcon_message)

            # patrolmssn.set_start_time(start_mission_time)
            cmd_str = "ScenEdit_SetMission('" + side_name + "','" + patrol_name + "',{starttime='" + start_mission_time + "'})"
            patrol_start_time = scenario.mozi_server.send_and_recv(cmd_str)
            print('patrol_start_time=', patrol_start_time)

    elif order_dic.get('order_type') == ORDER_TYPE.ADD_SEA_STRIKE_ORDER:
        side = scenario.get_side_by_name(side_name)
        contacts = side.contacts
        # contacts_temp = {k: v.strName for k, v in contacts.items()}
        # print('contacts_temp=', contacts_temp)
        strike_missions_dic = side.get_strike_missions()
        strike_mission_name = [mission.strName for mission in strike_missions_dic.values()]
        airs_dic = side.aircrafts
        strike_rule = order_dic.get('order_rule')
        strike_name = order_dic.get('order_name')
        if strike_name not in strike_mission_name:
            air_name = order_dic.get('unit_name')
            start_mission_time = order_dic.get('order_start_time')
            airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in air_name}
            # strkmssn_1 = side.add_mission_strike(strike_name, 2)
            strike_type = 'SEA'
            detail = f"{{type='{strike_type}'}}"
            cmd = "ReturnObj(ScenEdit_AddMission('{}','{}','{}',{}))".format(side.strGuid, strike_name, 'Strike', detail)
            scenario.mozi_server.throw_into_pool(cmd)
            add_strike_message = scenario.mozi_server.send_and_recv(cmd)
            print('打船指令=', add_strike_message)
            # 取消满足编队规模才能起飞的限制（任务条令）
            # strkmssn_1.set_one_third_rule(strike_rule.get('one_third_rule'))
            is_one_third = strike_rule.get('one_third_rule')
            cmd_3 = 'ScenEdit_SetMission("%s","%s", {oneThirdRule=%s})' % \
                    (side_name, strike_name, str(is_one_third).lower())
            scenario.mozi_server.throw_into_pool(cmd_3)
            one_third = scenario.mozi_server.send_and_recv(cmd_3)
            print('三分之一',one_third)
            # strkmssn_1.set_flight_size(strike_rule.get('flight_size'))
            flight_size = strike_rule.get('flight_size')
            cmd_4 = 'ScenEdit_SetMission("' + side_name + '","' + strike_name + '",{flightSize=' + str(
                flight_size) + '})'
            scenario.mozi_server.throw_into_pool(cmd_4)
            fl = scenario.mozi_server.send_and_recv(cmd_4)
            print('规模', fl)
            # strkmssn_1.set_flight_size_check(strike_rule.get('set_flight_size_check'))
            use_flight_size_check = strike_rule.get('set_flight_size_check')
            cmd_5 = 'ScenEdit_SetMission("' + side_name + '","' + strike_name + '", {''useFlightSize =' + str(
                use_flight_size_check).lower() + '})'
            scenario.mozi_server.throw_into_pool(cmd_5)
            flc = scenario.mozi_server.send_and_recv(cmd_5)
            print('规模检查', flc)
            targets = {k: v for k, v in contacts.items() for ship_name in order_dic.get('target') if ship_name in v.strName}
            for k, v in targets.items():
                # set_mark_contact设置目标对抗关系,H is 敌方
                # side.set_mark_contact(k, 'U')
                lua = "Hs_SetMarkContact('%s', '%s', '%s')" % (strike_name, k, 'U')
                mark_contact = scenario.mozi_server.send_and_recv(lua)
                print('对抗关系=', mark_contact)
            print('targets=', targets)
            for k, v in targets.items():
                # strkmssn_1.assign_unit_as_target(k)
                cmd = f"ScenEdit_AssignUnitAsTarget({{'{k}'}}, '{strike_name}')"
                scenario.mozi_server.throw_into_pool(cmd)
                assign_target = scenario.mozi_server.send_and_recv(cmd)
                print('打船分配目标=', assign_target)

            # strkmssn_1.assign_units(airs_strike)
            for k, v in airs_strike.items():
                cmd_2 = "ScenEdit_AssignUnitToMission('{}', '{}')".format(v.strGuid, strike_name)
                scenario.mozi_server.throw_into_pool(cmd_2)
                assign_fly = scenario.mozi_server.send_and_recv(cmd_2)
                print('打船分配飞机=', assign_fly)

            strike_plot_name = order_dic.get('strike_plot_name')
            strike_plot_point_list = order_dic.get('strike_plot_point')
            # side.add_plan_way(0, strike_plot_name)
            add_plan_way = scenario.mozi_server.send_and_recv("Hs_AddPlanWay('{}',{},'{}')".format(side.strName, 0, strike_plot_name))
            print('打船分配航线=', add_plan_way)

            for item in strike_plot_point_list:
                # side.add_plan_way_point(strike_plot_name, item['longitude'], item['latitude'])
                add_plan_way_point = scenario.mozi_server.send_and_recv(
                    "Hs_AddPlanWayPoint('{}','{}',{},{})".format(side.strGuid, strike_plot_name, item['longitude'],
                                                                 item['latitude']))
                print('打船航线分配点=', add_plan_way_point)

            # strkmssn_1.add_plan_way_to_mission(0, strike_plot_name)
            add_plan_way_to_mission = scenario.mozi_server.send_and_recv("Hs_AddPlanWayToMission('%s',%d,'%s')"
                                      % (strike_name, 0, strike_plot_name))
            print('把点分配给航线', add_plan_way_to_mission)

            # strkmssn_1.set_start_time(start_mission_time)
            cmd_str = "ScenEdit_SetMission('" + side_name + "','" + strike_name + "',{starttime='" + start_mission_time + "'})"
            strike_start_time = scenario.mozi_server.send_and_recv(cmd_str)
            print('strike_start_time=', strike_start_time)
def support_zone_for_two(side_name, scenario, support_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # rp15 = side.add_reference_point(side_name + str(i + 0), support_zone[0][0], support_zone[0][1])
    cmd15 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
            side_name + str(i + 0), support_zone[0][0], support_zone[0][1])
    scenario.mozi_server.send_and_recv(cmd15)
    # rp16 = side.add_reference_point(side_name + str(i + 1), support_zone[1][0], support_zone[1][1])
    cmd16 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + str(i + 1),
                                                                                               support_zone[1][0],
                                                                                               support_zone[1][1])
    scenario.mozi_server.send_and_recv(cmd16)
    # rp17 = side.add_reference_point(side_name + str(i + 2), support_zone[2][0], support_zone[2][1])
    cmd17 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + str(i + 2),
                                                                                               support_zone[2][0],
                                                                                               support_zone[2][1])
    scenario.mozi_server.send_and_recv(cmd17)
    # rp18 = side.add_reference_point(side_name + str(i + 3), support_zone[3][0], support_zone[3][1])
    cmd18 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + str(i + 3),
                                                                                               support_zone[3][0],
                                                                                               support_zone[3][1])
    scenario.mozi_server.send_and_recv(cmd18)
    point_list.append(side_name + str(i + 0))
    point_list.append(side_name + str(i + 1))
    point_list.append(side_name + str(i + 2))
    point_list.append(side_name + str(i + 3))
    return point_list

def create_patrol_zone(side_name, scenario, patrol_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # rp1 = side.add_reference_point(side_name + 'xlrp' + str(i + 0), patrol_zone[0][0], patrol_zone[0][1])
    cmd15 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'xlrp' + str(i + 0),
                                                                                               patrol_zone[0][0],
                                                                                               patrol_zone[0][1])
    patrol_zone_point_1 = scenario.mozi_server.send_and_recv(cmd15)
    print('patrol_zone_point_1=', patrol_zone_point_1)
    # rp2 = side.add_reference_point(side_name + 'xlrp' + str(i + 1), patrol_zone[1][0], patrol_zone[1][1])
    cmd16 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'xlrp' + str(
                                                                                                   i + 1),
                                                                                               patrol_zone[1][0],
                                                                                               patrol_zone[1][1])
    patrol_zone_point_2 = scenario.mozi_server.send_and_recv(cmd16)
    print('patrol_zone_point_2=', patrol_zone_point_2)
    # rp3 = side.add_reference_point(side_name + 'xlrp' + str(i + 2), patrol_zone[2][0], patrol_zone[2][1])
    cmd17 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'xlrp' + str(
                                                                                                   i + 2),
                                                                                               patrol_zone[2][0],
                                                                                               patrol_zone[2][1])
    patrol_zone_point_3 = scenario.mozi_server.send_and_recv(cmd17)
    print('patrol_zone_point_3=', patrol_zone_point_3)
    # rp4 = side.add_reference_point(side_name + 'xlrp' + str(i + 3), patrol_zone[3][0], patrol_zone[3][1])
    cmd18 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'xlrp' + str(
                                                                                                   i + 3),
                                                                                               patrol_zone[3][0],
                                                                                               patrol_zone[3][1])
    patrol_zone_point_4 = scenario.mozi_server.send_and_recv(cmd18)
    print('patrol_zone_point_4=', patrol_zone_point_4)
    point_list.append(side_name + 'xlrp' + str(i + 0))
    point_list.append(side_name + 'xlrp' + str(i + 1))
    point_list.append(side_name + 'xlrp' + str(i + 2))
    point_list.append(side_name + 'xlrp' + str(i + 3))
    return point_list
def creat_prosecution_area(side_name, scenario, prosecution_zone, i):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    # jj1 = side.add_reference_point(side_name + 'jjrp' + str(i + 0), prosecution_zone[0][0], prosecution_zone[0][1])
    cmd15 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'jjrp' + str(
                                                                                                   i + 0),
                                                                                               prosecution_zone[0][0],
                                                                                               prosecution_zone[0][1])
    scenario.mozi_server.send_and_recv(cmd15)
    # jj2 = side.add_reference_point(side_name + 'jjrp' + str(i + 1), prosecution_zone[1][0], prosecution_zone[1][1])
    cmd16 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'jjrp' + str(
                                                                                                   i + 1),
                                                                                               prosecution_zone[1][0],
                                                                                               prosecution_zone[1][1])
    scenario.mozi_server.send_and_recv(cmd16)
    # jj3 = side.add_reference_point(side_name + 'jjrp' + str(i + 2), prosecution_zone[2][0], prosecution_zone[2][1])
    cmd17 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'jjrp' + str(
                                                                                                   i + 2),
                                                                                               prosecution_zone[2][0],
                                                                                               prosecution_zone[2][1])
    scenario.mozi_server.send_and_recv(cmd17)
    # jj4 = side.add_reference_point(side_name + 'jjrp' + str(i + 3), prosecution_zone[3][0], prosecution_zone[3][1])
    cmd18 = "ReturnObj(ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s}))" % (side_name,
                                                                                               side_name + 'jjrp' + str(
                                                                                                   i + 3),
                                                                                               prosecution_zone[3][0],
                                                                                               prosecution_zone[3][1])
    scenario.mozi_server.send_and_recv(cmd18)
    point_list.append(side_name + 'jjrp' + str(i + 0))
    point_list.append(side_name + 'jjrp' + str(i + 1))
    point_list.append(side_name + 'jjrp' + str(i + 2))
    point_list.append(side_name + 'jjrp' + str(i + 3))
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
        # airs_dic = side.aircrafts
        # airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in [
        #                         "F-16A #7",
        #                         "F-16A #06"
        #                     ]}
        # for v in airs_strike.values():
        #     print('飞机名字经纬度', v.strName, v.dLatitude, v.dLongitude)
        for patrol_mission in patrol_missions:
            if patrol_mission.strName == patrol_name:
                doctrine_xl1 = patrol_mission.get_doctrine()
                # doctrine_xl1.set_weapon_state_for_aircraft(patrol_rule.get('weapon_state_for_aircraft'))
                cmd = "ScenEdit_SetDoctrine({side ='%s', mission = '%s'}, {weapon_state_planned ='%s'})" % (
                    patrol_mission.m_Side, patrol_mission.strGuid, patrol_rule.get('weapon_state_for_aircraft'))
                scenario.mozi_server.throw_into_pool(cmd)
                scenario.mozi_server.send_and_recv(cmd)
                # doctrine_xl1.set_weapon_state_for_air_group(patrol_rule.get('weapon_state_for_air_group'))
                cmd = "ScenEdit_SetDoctrine({side ='%s', mission = '%s'}, {weapon_state_rtb ='%s'})" % (
                    patrol_mission.m_Side, patrol_mission.strGuid, patrol_rule.get('weapon_state_for_air_group'))
                scenario.mozi_server.throw_into_pool(cmd)
                scenario.mozi_server.send_and_recv(cmd)
                # doctrine_xl1.gun_strafe_for_aircraft('1')
                cmd = "ScenEdit_SetDoctrine({side ='%s', mission = '%s'}, {gun_strafing ='%s'})" % (
                    patrol_mission.m_Side, patrol_mission.strGuid, '1')
                scenario.mozi_server.throw_into_pool(cmd)
                scenario.mozi_server.send_and_recv(cmd)
                # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
                # edit_weapon_doctrine(doctrine=doctrine_xl1, rule=patrol_rule)
    elif order_dic.get('order_type') == ORDER_TYPE.ADD_SEA_STRIKE_ORDER:
        strike_rule = order_dic.get('order_rule')
        strike_name = order_dic.get('order_name')
        airs_dic = side.aircrafts
        airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in [
                                "F-16A #4"
                                ]}
        for v in airs_strike.values():
            print('飞机经纬度',v.strName, v.dLatitude, v.dLongitude)

        for strike_mission in strike_missions:
            if strike_mission.strName == strike_name:
                print('strike_name=', strike_name)
                doctrine_sk1 = strike_mission.get_doctrine()
                # doctrine_sk1.set_weapon_state_for_aircraft(strike_rule.get('weapon_state_for_aircraft'))
                cmd = "ScenEdit_SetDoctrine({side ='%s', mission = '%s'}, {weapon_state_planned ='%s'})" % (
                    strike_mission.m_Side, strike_mission.strGuid, strike_rule.get('weapon_state_for_aircraft'))
                scenario.mozi_server.throw_into_pool(cmd)
                weapon_state_for_aircraft = scenario.mozi_server.send_and_recv(cmd)
                print('武器个体状态=', weapon_state_for_aircraft)
                # doctrine_sk1.set_weapon_state_for_air_group(strike_rule.get('weapon_state_for_air_group'))
                cmd = "ScenEdit_SetDoctrine({side ='%s', mission = '%s'}, {weapon_state_rtb ='%s'})" % (
                    strike_mission.m_Side, strike_mission.strGuid, strike_rule.get('weapon_state_for_air_group'))
                scenario.mozi_server.throw_into_pool(cmd)
                weapon_state_for_air_group = scenario.mozi_server.send_and_recv(cmd)
                print('武器编组状态', weapon_state_for_air_group)

                # edit_anti_ship_weapon_doctrine(doctrine=doctrine_sk1, rule=strike_rule)
    elif order_dic.get('order_type') == ORDER_TYPE.UPDATE_REFENCE_POINT:
        current_simtime = scenario.get_current_time()
        # airs_dic = side.aircrafts
        # airs_strike = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in [
        #     "EC-130H #2"
        # ]}
        # for v in airs_strike.values():
        #     print('飞机名字经纬度', v.strName, v.dLatitude, v.dLongitude)
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
        # side.set_reference_point(old_name, new_point[0], new_point[1])
        set_str = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
            side.strName, old_name, new_point[0], new_point[1])
        updata_support_zone = scenario.mozi_server.send_and_recv(set_str)
        print('updata_support_zone=', updata_support_zone)