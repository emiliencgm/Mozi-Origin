# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
def edit_side_doctrine(side):
    doctrine = side.get_doctrine()
    # 对空自由开火
    doctrine.set_weapon_control_status('weapon_control_status_air',0)
    # 对面自由开火
    doctrine.set_weapon_control_status('weapon_control_status_surface', 0)
    doctrine.ignore_plotted_course('yes')
    doctrine.set_fuel_state_for_aircraft('Bingo')
    doctrine.set_fuel_state_for_air_group('YesLeaveGroup')
    doctrine.set_weapon_state_for_aircraft('2002')
    doctrine.set_weapon_state_for_air_group('YesLastUnit')
    doctrine.set_em_control_status('Radar','Passive')
    doctrine.set_em_control_status('Sonar', 'Passive')
    doctrine.set_em_control_status('OECM', 'Passive')
    # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
    doctrine.set_weapon_release_authority('816','2999','2','1','max','max','false')
    doctrine.set_weapon_release_authority('816', '3101', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3102', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3103', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3000', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3104', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3105', '0', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3106', '0', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3107', '0', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('816', '3108', '0', '1', 'max', 'max', 'false')
    # AIM-120C-7
    doctrine.set_weapon_release_authority('718', '1999', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2000', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2001', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2002', '2', '1', 'max', 'max', 'false')
    # doctrine.set_weapon_release_authority('718', '2021', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2031', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2100', '0', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('718', '2200', '0', '1', 'max', 'max', 'false')
    # AIM-9M
    doctrine.set_weapon_release_authority('1384', '1999', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2000', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2001', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2002', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2021', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2031', '2', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2100', '0', '1', 'max', 'max', 'false')
    doctrine.set_weapon_release_authority('1384', '2200', '0', '1', 'max', 'max', 'false')

def add_point(a,z,point,side,side_name):
    area = []
    name = a
    while name < z:
        for k in point:
            side.add_reference_point(str(name),k[0],k[1])
            area.append('f16编队' + str(name))
            name += 1
    return area

# 创建巡逻任务
def create_patrol_mission(side_name,mission_name,patrol_type_num,patrol_area,scenario,units,group_size):
    side = scenario.get_side_by_name(side_name)
    patrol_mission = CPatrolMission(scenario.strGuid,scenario.mozi_server,scenario.situation)
    patrol_mission.strName = mission_name
    patrol_mission.m_Side = side_name
    airs_dic = side.aircrafts
    air_strname = [v.strName for v in airs_dic.values()]
    # with open('air_name.txt','w') as f:
    #     print(air_strname,file=f)
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 9}
    airs_xl1 = {k: airs[k] for k, v in airs.items() if v.strName in units}
    patrolmssn = side.add_mission_patrol(mission_name, patrol_type_num, patrol_area)
    patrol_mission.assign_units(airs_xl1)
    patrol_mission.set_is_active('true')
    patrol_mission.set_one_third_rule('false')
    patrol_mission.set_opa_check('true')
    patrol_mission.set_wwr_check('true')
    patrol_mission.set_emcon_usage('false')
    patrol_mission.set_flight_size(group_size)
    patrol_mission.set_flight_size_check('false')

    scenario.mozi_server.set_key_value(f'{side_name}巡逻任务已创建', 'Yes')

def add_groups(side_name,scenario,units):
    # 创建编队,没用
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 3}
    airs_xl1 = [k for k, v in airs.items() if v.strName in units]
    side.add_group(airs_xl1)
    print('创建编队完成')


def edit_patrol_mission(patrol_mission):
    patrol_mission.set_throttle_transit('Cruise')
    patrol_mission.set_throttle_station('Cruise')
    patrol_mission.set_throttle_attack('Cruise')

def edit_mission_doctrine(side,mission_name):
    patrol_mission = side.get_missions_by_name(mission_name)
    doctrines = patrol_mission.get_doctrine()
    doctrines.set_fuel_state_for_air_group('YesLeaveGroup')
    doctrines.set_weapon_state_for_air_group('YesLastUnit')
    doctrines.set_emcon_according_to_superiors('yes','false')

def edit_unit_doctrine(unit):
    doctrine = unit.get_doctrine()
    doctrine.set_em_control_status('OECM','Active')

def get_group(side,units_name):
    # 没用
    for v in units_name:
        all_groups = side.get_groups()
        print('all_groups=',all_groups)
        for k,a_group in all_groups.items():
            a_group_dic = a_group.get_units()
            for k,unit in a_group_dic.items():
                if v in unit.strName:
                    return a_group

def get_lead(a_group,side):
    # 没用
    lead = side.get_unit_by_guid(a_group.m_GroupLead)
    print('已获取领队',lead.strName)
    return lead


def get_aircraft(side,unit_name):
    airs = side.aircrafts
    for k,v in airs.items():
        if v.strName in unit_name:
            return v


def return_to_airport(EA,group):
    i = EA.get_status_type()
    if i == 'InAirRTB':
        # units = group.get_units()
        for v in group.values():
            v.return_to_base()
        print('电子战机已返航，编队已返航')

def judge_target(unit,side):
    # 没用
    target = []
    target_guid = unit.m_AITargets
    if len(target_guid) != 0:
        contact_dic = side.contacts
        for k , v in contact_dic.items():
            if k == target_guid:
                distance_km = get_horizontal_distance((unit.dLatitude,unit.dLongitude),(v.dLatitude,v.dLongitude))
                target.extend([v.strName,distance_km,v.dLatitude,v.dLongitude])
                return target
    else:
        return False


def judge_space(core,group,interval):
    judge = []
    # group_dic = group.get_units()
    group_dic = group
    for k,unit in group_dic.items():
        if unit:
            distance_km = get_horizontal_distance((core.dLatitude,core.dLongitude),(unit.dLatitude,unit.dLongitude))
            distance_m = 1000 * distance_km
            print(core.strName,'坐标','(',core.dLatitude,',',core.dLongitude,')',' ',
                  unit.strName,'坐标','(',unit.dLatitude,',',unit.dLongitude,')',' ',
                  unit.strName,'距',core.strName,': ',distance_m,'米')
            if distance_m > interval:
                judge.append('F')
    if 'F' in judge:
        return False
    else:
        return True

def approach(group,core,speed):
    group_dic = group
    for k,unit in group_dic.items():
        if unit:
            core.plot_course([(core.dLatitude,core.dLongitude)])
            core.set_desired_speed(speed)
            unit.plot_course([(core.dLatitude,core.dLongitude)])
            unit.set_desired_speed(speed)

def follow(group,next_point,core,speed):
    group_dic = group
    for k,unit in group_dic.items():
        if unit:
            if len(next_point) != 0:
                core.plot_course([next_point])
                core.set_desired_speed(speed)
                unit.plot_course([next_point])
                unit.set_desired_speed(speed)
                print(core.strName,'正与',unit.strName,'向给定航路点',next_point,'飞行')
            else:
                next_point_list = core.get_way_points_info()
                if len(next_point_list) != 0:
                    next_point_dic = next_point_list[0]
                    new_next_point = []
                    for k ,v in next_point_dic.items():
                        if k == 'latitude':
                            new_next_point.append(v)
                    for k,v in next_point_dic.items():
                        if k == 'longitude':
                            new_next_point.append(v)
                    core.plot_course([(new_next_point[0],new_next_point[1])])
                    core.set_desired_speed(speed)
                    unit.plot_course([(new_next_point[0],new_next_point[1])])
                    unit.set_desired_speed(speed)
                    print(core.strName, '正与', unit.strName, '向自定航路点', new_next_point, '飞行')

def ajm_consume(unit_or_group):

    for unit in unit_or_group.values():
        weapon = unit.get_weapon_infos()
        print('weapon length', len(weapon))
        if len(weapon) == 6 or len(weapon) == 5:
            return True
        else:
            print('弹药已耗尽')
            return False

def ecm_2(side,mission_name,group,EA,afterburner,interval,patrol_area,cordon_area,EW=None):
    contacts = side.contacts
    distance_list = []
    contact_list = []
    patrol_mission = side.get_missions_by_name(mission_name)
    # patrol_mission.unassign_unit(EA.strName)
    # patrol_mission.unassign_unit(group.strGuid)
    # lead = get_lead(group,side)
    return_to_airport(EA,group)
    spacing = judge_space(EA,group,interval)
    if spacing:
        if contacts:
            for k,v in contacts.items():
                if cordon_area[0] < v.dLatitude < cordon_area[1] and cordon_area[2] < v.dLongitude < cordon_area[3]:
                    distance_km = get_horizontal_distance((EA.dLatitude,EA.dLongitude),(v.dLatitude,v.dLongitude))
                    distance_list.append(distance_km)
                    contact_list.append(v)
            if distance_list:
                distance_min = min(distance_list)
                print('distance_min=',distance_min)
                order = distance_list.index(distance_min)
                contact = contact_list[order]
                # print('领队：',lead.strName,'距目标: ',contact.strName,distance_min,'公里')
                print('contact.strName=',contact.strName)
                if '航空母舰' in contact.strName and afterburner[0] < distance_min < afterburner[1]:
                    follow(group,(contact.dLatitude+0.5,contact.dLongitude-0.5),EA,1700.0)
                    print('打开加力')
                else:
                    follow(group, (contact.dLatitude+0.5, contact.dLongitude-0.5), EA, 890.0)
                    if EW is not None:
                        EW.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])
                    # follow(group, (), EA, 890.0)
            else:
                print('当前警戒区内无目标')
                EA.plot_course([((patrol_area[0] + patrol_area[1]) / 2,(patrol_area[2] + patrol_area[3]) / 2)])
                if EW is not None:
                    EW.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])
        else:
            follow(group,(),EA,890.0)
            print('当前我军无目标')
            EA.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])
            if EW is not None:
                EW.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])
    else:
        approach(group,EA,890.0)
        EA.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])
        if EW is not None:
            EW.plot_course([((patrol_area[0] + patrol_area[1]) / 2, (patrol_area[2] + patrol_area[3]) / 2)])



