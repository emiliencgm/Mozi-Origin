# by aie


import re
from mozi_ai_sdk.btmodel.bt import utils
from mozi_ai_sdk.feihai_blue.utils import function
from mozi_simu_sdk.args import Throttle
from mozi_simu_sdk.geo import get_horizontal_distance, get_end_point
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission

def edit(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    patrol_mission = side.get_patrol_missions()
    if len(patrol_mission) != 0:
        for k,v in patrol_mission.items():
            if v.m_StationThrottle_Aircraft == 2:
                return True
            else:
                # point = [(19.9345274245098,124.017702269376),(18.8527511210967,123.27120415328),(19.2245416178875,124.282096641003),(18.854,123.272)]
                # cordon_area = function.add_point(5,9,point,side,side_name)
                # transit = [Throttle.Cruise,13000.0]
                # station = [Throttle.Cruise,13000.0]
                # attack = [Throttle.Cruise,13000.0]
                function.edit_patrol_mission(v)
        return False
    else:
        function.edit_side_doctrine(side)
        point = [(21.3393208707725, 123.455654519338), (19.8005959781429, 122.481969737532),(19.128692115499, 122.815487295963), (20.7296179415939, 124.75271117856)]
        patrol_area = function.add_point(1,5,point,side,side_name)
        units_2 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04', 'F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09','EC-130H #2']
        function.create_patrol_mission(side_name,'f16编队', 1, patrol_area, scenario, units_2, 3)
        units_1 = ['F-16A #1', 'F-16A #2', 'F-16A #3', 'F-16A #4', 'F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8', 'F-16A #9', 'EC-130H #1', 'E-2K #1']
        point_1 = [(22.181378549063, 121.049571002033),(22.1691773335694, 124.194508316028),(20.6722068167905, 121.062131270682),(20.6370176672735, 124.156690488837)]
        patrol_area_1 = function.add_point(5, 9, point_1, side, side_name)
        function.create_patrol_mission(side_name, '伴随干扰进攻', 0, patrol_area_1, scenario, units_1, 3)
        return False



def unit_and_mission(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    patrol_missions = side.get_patrol_missions()
    patrol_mission = [ v for v in patrol_missions.values() if 'f16编队' in v.strName or '伴随干扰进攻' in v.strName]
    if len(patrol_mission) != 0:
        doctrine_1 = patrol_mission[0].get_doctrine()
        doctrine_2 = patrol_mission[1].get_doctrine()
        # 3 = 当单元达到返回基地油量状态时，脱离编组返回基地
        if doctrine_1.m_BingoJokerRTB == 3 and doctrine_2.m_BingoJokerRTB == 3:
            return True
        else:
            unit_name = ['EC-130H #1']
            unit = function.get_aircraft(side,unit_name)
            function.edit_unit_doctrine(unit)
            unit_name_2 = ['EC-130H #2']
            unit_2 = function.get_aircraft(side,unit_name_2)
            function.edit_unit_doctrine(unit_2)
            mission_name = 'f16编队'
            function.edit_mission_doctrine(side,mission_name)
            mission_name_2 = '伴随干扰进攻'
            function.edit_mission_doctrine(side,mission_name_2)
            return False


def air_combat(side_name, scenario):
    side = scenario.get_side_by_name(side_name)
    airs_dic = side.aircrafts
    afterburner = [145,185]
    interval = 2000
    # patrol_area = [19.0,21.0,123.0,124.0]
    patrol_area = [21.8318169475752, 20.3872237408008, 122.11731231479, 123.362734539741]
    cordon_area = [17.0,23.0,120.0,126.0]
    mission_name_2 = 'f16编队'
    mission_name_1 = '伴随干扰进攻'
    group_name_2 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04', 'F-16A #05', 'F-16A #06', 'F-16A #07', 'F-16A #08', 'F-16A #09']
    group_name_1 = ['F-16A #1', 'F-16A #2', 'F-16A #3', 'F-16A #4', 'F-16A #5', 'F-16A #6', 'F-16A #7', 'F-16A #8',
                 'F-16A #9']
    airs = {k: v for k, v in airs_dic.items() if int(v.strName.split('#')[1]) <= 9}
    group = {k: airs[k] for k, v in airs.items() if v.strName in group_name_1}
    group_2 = {k: airs[k] for k, v in airs.items() if v.strName in group_name_2}
    if group:
        EA_name = ['EC-130H #1']
        EA = function.get_aircraft(side,EA_name)
        if EA:
            EW_name = ['E-2K #1']
            EW = function.get_aircraft(side,EW_name)
            if EW:
                print('战术：伴随干扰')
                function.return_to_airport(EA,group)
                AGM = function.ajm_consume(group)
                if AGM:
                    print('进入ecm_2函数')
                    function.ecm_2(side, mission_name_1, group, EA, afterburner, interval, patrol_area, cordon_area,EW)
                else:
                    EA.return_to_base()
    if group_2:
        EA_name_2 = ['EC-130H #2']
        EA_2 = function.get_aircraft(side, EA_name_2)
        if EA_2:
            print('战术：伴随干扰2')
            function.return_to_airport(EA_2, group_2)
            AGM = function.ajm_consume(group_2)
            if AGM:
                print('进入ecm_2函数_2')
                function.ecm_2(side, mission_name_2, group_2, EA_2, afterburner, interval, patrol_area, cordon_area)
            else:
                EA_2.return_to_base()
    return True
