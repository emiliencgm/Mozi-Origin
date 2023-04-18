# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission


# lst_1 = ['F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','EC-130H #2']
# lst_1 = [  'EC-130H #2']
# lst_1 到 4是第一波次编组
lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9']
lst_2 = ['F-16A #07', 'F-16A #08', 'F-16A #09']
lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03']
lst_4 = ['F-16A #04', 'F-16A #05', 'F-16A #06']
# lst_5 到 6是第二波次编组
lst_5 = ['F-16A #1', 'F-16A #2','F-16A #3']
lst_6 = ['F-16A #4', 'F-16A #5', 'F-16A #6']
lst_7 = ['EC-130H #1']
lst_8 = ['EC-130H #2']
lst_9 = ['E-2K #1']
# lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9', 'EC-130H #1', 'E-2K #1']

def get_group_first(side_name, scenario):
    # 先让飞机起飞，设置单机出动，给定航路点，然后形成第一波次的4个编组，返回的编组的对象
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    # 交战中线的起始点
    start_point = (19.3293120782526, 121.421150338814)
    end_point = (22.6183323190618, 125.160161409173)
    # 交战中线的中点作为飞机的航路点
    middiel_point = ((start_point[0] + end_point[0]) / 2, (end_point[1] + start_point[1]) / 2)
    all_first_group_list = []
    airs_1_for_key = [k for k, v in airs_dic.items() if v.strName in lst_1]
    air_group_1 = side.add_group(airs_1_for_key)
    airs_2_for_key = [k for k, v in airs_dic.items() if v.strName in lst_2]
    air_group_2 = side.add_group(airs_2_for_key)
    airs_3_for_key = [k for k, v in airs_dic.items() if v.strName in lst_3]
    air_group_3 = side.add_group(airs_3_for_key)
    airs_4_for_key = [k for k, v in airs_dic.items() if v.strName in lst_4]
    air_group_4 = side.add_group(airs_4_for_key)
    all_first_group_list.append(air_group_1)
    all_first_group_list.append(air_group_2)
    all_first_group_list.append(air_group_3)
    all_first_group_list.append(air_group_4)
    print('all_first_group_list=',all_first_group_list)
    return all_first_group_list

def get_group_second(side_name, scenario):
    # 形成第二波次的2个编组，返回的编组的对象
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    # 交战中线的起始点
    start_point = (19.3293120782526, 121.421150338814)
    end_point = (22.6183323190618, 125.160161409173)
    # 交战中线的中点作为飞机的航路点
    middiel_point = ((start_point[0] + end_point[0]) / 2, (end_point[1] + start_point[1]) / 2)
    all_second_group_list = []
    airs_5_for_key = [k for k, v in airs_dic.items() if v.strName in lst_5]
    for key in airs_5_for_key:
        airs_dic[key].set_single_out()
        airs_dic[key].plot_course([middiel_point])
    air_group_1 = side.add_group(airs_5_for_key)
    airs_6_for_key = [k for k, v in airs_dic.items() if v.strName in lst_6]
    for key in airs_6_for_key:
        airs_dic[key].set_single_out()
        airs_dic[key].plot_course([middiel_point])
    air_group_2 = side.add_group(airs_6_for_key)
    all_second_group_list.append(air_group_1)
    all_second_group_list.append(air_group_2)
    return all_second_group_list


def send_strike_order(side_name, scenario):
    # 给4个编队的飞机下达打击指令，让飞机动起来，原来的获取编队下的成员函数不能使
    # 只能重新获取飞机下达指令
    side = scenario.get_side_by_name(side_name)
    groups = side.get_groups()
    print('编组长度=',len(groups))

    airs_dic = side.aircrafts
    airs_1 = {k: v for k, v in airs_dic.items() if v.strName in lst_1}
    airs_1_list = [k for k, v in airs_dic.items() if v.strName in lst_1]
    airs_2 = {k: v for k, v in airs_dic.items() if v.strName in lst_2}
    airs_2_list = [k for k, v in airs_dic.items() if v.strName in lst_2]
    airs_3 = {k: v for k, v in airs_dic.items() if v.strName in lst_3}
    airs_4 = {k: v for k, v in airs_dic.items() if v.strName in lst_4}
    mssnSitu = side.strikemssns
    red_side = scenario.get_side_by_name('红方')
    contacts = red_side.aircrafts
    # contacts = side.contacts
    target_1 = {k: v for k, v in contacts.items() if '米格' in v.strName and '在空' in v.strActiveUnitStatus}
    print('target1=', target_1)
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
        strkmssn_1 = side.add_mission_strike('strike1', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        side.air_group_out(airs_1_list)
        strkmssn_1.set_flight_size(3)
        strkmssn_1.set_flight_size_check('false')
        if len(target_1) != 0:
            for k, v in target_1.items():
                strkmssn_1.assign_unit_as_target(k)
        side.add_plan_way(0, '航线2')
        strkmssn_1.add_plan_way_to_mission(0, '航线2')
        strkmssn_1.assign_units(airs_1)
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike2'}.__len__() == 0:
        strkmssn_2 = side.add_mission_strike('strike2', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        side.air_group_out(airs_2_list)
        strkmssn_2.set_flight_size(3)
        strkmssn_2.set_flight_size_check('false')
        if len(target_1) != 0:
            for k, v in target_1.items():
                strkmssn_2.assign_unit_as_target(k)
        side.add_plan_way(0, '航线2')
        strkmssn_2.add_plan_way_to_mission(0, '航线2')
        strkmssn_2.assign_units(airs_2)
    '''
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike3'}.__len__() == 0:
        strkmssn_3 = side.add_mission_strike('strike3', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_3.set_flight_size(3)
        strkmssn_3.set_flight_size_check('false')
        if len(target_1) != 0:
            for k, v in target_1.items():
                strkmssn_3.assign_unit_as_target(k)
        side.add_plan_way(0, '航线2')
        strkmssn_3.add_plan_way_to_mission(0, '航线2')
        strkmssn_3.assign_units(airs_3)
    if {k: v for k, v in mssnSitu.items() if v.strName == 'strike4'}.__len__() == 0:
        strkmssn_4 = side.add_mission_strike('strike4', 0)
        # 取消满足编队规模才能起飞的限制（任务条令）
        strkmssn_4.set_flight_size(3)
        strkmssn_4.set_flight_size_check('false')
        if len(target_1) != 0:
            for k, v in target_1.items():
                strkmssn_4.assign_unit_as_target(k)
        side.add_plan_way(0, '航线2')
        strkmssn_4.add_plan_way_to_mission(0, '航线2')
        strkmssn_4.assign_units(airs_4)
    '''

    print('创建空中截击任务完毕,不重复创建')


def set_group_attribute(side_name, scenario, all_group_list):
    # 设置编队队形，领队
    # 先判断是否全部形成编队，只有形成编队才设置队形，领队
    # 交战前各三机编队只有长机雷达开机，其他飞机雷达、无线电静默
    side = scenario.get_side_by_name(side_name)
    all_group_list_flag = all([i is not None for i in all_group_list])
    group_lead_name = ['F-16A #7', 'F-16A #07', 'F-16A #01', 'F-16A #04']
    # print('all_group_list_flag=',all_group_list_flag)
    if all_group_list_flag:
        for group, lead_name in zip(all_group_list, group_lead_name):
            group.set_formation_group_lead(lead_name)
            group.set_formation_group_member(lead_name, 'Rotating', 0, 1)

def add_support_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    airs_support1 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_9}
    airs_support2 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_7}
    airs_support3 = {k: airs_dic[k] for k, v in airs_dic.items() if v.strName in lst_8}
    support_missions_dic = side.get_support_missions()
    support_missions_1 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '1']
    support_missions_2 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '2']
    support_missions_3 = [v for v in support_missions_dic.values() if v.strName == side_name + 'support' + '3']
    if len(support_missions_1) == 0:
        for air in airs_support1.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('Radar', 'Active')
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
    if len(support_missions_2) == 0:
        for air in airs_support2.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
        support_point_list = support_zone_for_ec_1(side_name, scenario)
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
    if len(support_missions_3) == 0:
        for air in airs_support3.values():
            doctrine = air.get_doctrine()
            doctrine.set_em_control_status('OECM', 'Active')
        support_point_list = support_zone_for_ec_2(side_name, scenario)
        for point in support_point_list:
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
def support_zone_for_two(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(21.8764427622847, 121.330904108449), (21.8335734773605, 121.478618597081),
               (21.6920926322308, 121.580152213845), (21.6899037180596, 121.405076571889)]
    rp1 = side.add_reference_point(side_name + 'rp1', point_1[0][0], point_1[0][1])
    rp2 = side.add_reference_point(side_name + 'rp2', point_1[1][0], point_1[1][1])
    rp3 = side.add_reference_point(side_name + 'rp3', point_1[2][0], point_1[2][1])
    rp4 = side.add_reference_point(side_name + 'rp4', point_1[3][0], point_1[3][1])
    point_list.append([rp1, rp2, rp3, rp4])
    return point_list

def support_zone_for_ec_1(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(21.8764427622847, 121.330904108449), (21.8335734773605, 121.478618597081),
               (21.6920926322308, 121.580152213845), (21.6899037180596, 121.405076571889)]
    # latitude = '20.7410544182443', longitude = '121.447025319445'
    # latitude = '20.7337623597836', longitude = '121.674065079492'
    # latitude = '20.6002999289788', longitude = '121.667517650411'
    # latitude = '20.6072227693128', longitude = '121.420109091165'

    point_1 = [(20.7410544182443, 121.447025319445), (20.7337623597836, 121.674065079492),
               (20.6002999289788, 121.667517650411), (20.6072227693128, 121.420109091165)]
    rp5 = side.add_reference_point(side_name + 'rp5', point_1[0][0], point_1[0][1])
    rp6 = side.add_reference_point(side_name + 'rp6', point_1[1][0], point_1[1][1])
    rp7 = side.add_reference_point(side_name + 'rp7', point_1[2][0], point_1[2][1])
    rp8 = side.add_reference_point(side_name + 'rp8', point_1[3][0], point_1[3][1])
    point_list.append([rp5, rp6, rp7, rp8])
    return point_list


def support_zone_for_ec_2(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    point_list = []
    point_1 = [(21.8764427622847, 121.330904108449), (21.8335734773605, 121.478618597081),
               (21.6920926322308, 121.580152213845), (21.6899037180596, 121.405076571889)]

    point_1 = [(22.3030800823733, 122.318311825324), (22.2785857178454, 122.537917506491),
               (22.0932400899911, 122.528346169613), (22.0887743118036, 122.294428777883)]
    rp9 = side.add_reference_point(side_name + 'rp9', point_1[0][0], point_1[0][1])
    rp10 = side.add_reference_point(side_name + 'rp10', point_1[1][0], point_1[1][1])
    rp11 = side.add_reference_point(side_name + 'rp11', point_1[2][0], point_1[2][1])
    rp12 = side.add_reference_point(side_name + 'rp12', point_1[3][0], point_1[3][1])
    point_list.append([rp9, rp10, rp11, rp12])
    return point_list

