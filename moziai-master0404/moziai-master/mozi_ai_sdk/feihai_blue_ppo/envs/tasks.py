# 时间 ： 2020/8/29 20:34
# 作者 ： Dixit
# 文件 ： tasks.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司
# 实体是随机选的
# 没有攻击性巡逻任务，删
from mozi_ai_sdk.btmodel.bt import utils
import re
import random
import itertools
import uuid
from collections import namedtuple
import datetime
import numpy as np
from itertools import chain
from mozi_simu_sdk.mssnpatrol import CPatrolMission
from mozi_simu_sdk.mssnstrike import CStrikeMission
from mozi_ai_sdk.feihai_blue_ppo.envs.utils import *
from mozi_ai_sdk.feihai_blue_ppo.envs.spaces.mask_discrete import MaskDiscrete

# mission_type = {0: 'NoneValue : 未知',
#                 1: 'Strike : 打击/截击任务',
#                 2: 'Patrol : 巡逻任务',
#                 3: 'Support : 支援任务',
#                 4: 'Ferry : 转场任务',
#                 5: 'Mining : 布雷任务',
#                 6: 'MineClearing : 扫雷任务',
#                 7: 'Escort : 护航任务',
#                 8: 'Cargo : 投送任务'}
#
# strike_type = {0: 'AIR : 空中拦截',
#                1: 'LAND : 对陆打击',
#                2: 'SEA : 对海打击',
#                3: 'SUB : 对陆潜打击'}
#
# patrol_type = {0: 'AAW : 空战巡逻',
#                1: 'SUR_SEA : 反面(海)巡逻',
#                2: 'SUR_LAND : 反面(陆)巡逻',
#                3: 'SUR_MIXED : 反面(混)巡逻',
#                4: 'SUB : 反潜巡逻',
#                5: 'SEAD : 压制敌防空巡逻',
#                6: 'SEA : 海上控制巡逻'}
Function = namedtuple('Function', ['type', 'function', 'is_valid'])


class Task(object):
    def __init__(self, env, scenario, sideName):
        self.scenario = scenario
        self.time = self.scenario.m_Duration.split('@')  # 想定总持续时间
        self.m_StartTime = self.scenario.m_StartTime  # 想定开始时间
        self.m_Time = self.scenario.m_Time  # 想定当前时间
        self._env = env
        self.sideName = sideName
        self.side = self.scenario.get_side_by_name(self.sideName)
        # self.defend_zones = [['AI-AO-1', 'rp2', 'rp3', 'rp4'],
        #                      ['rp2', 'AI-AO-2', 'rp5', 'rp3'],
        #                      ['rp3', 'rp5', 'AI-AO-3', 'rp6'],
        #                      ['rp4', 'rp3', 'rp6', 'AI-AO-4']]
        # self.defend_zones = [['AI-AO-1', 'rp2', 'rp3', 'rp4'],
        #                      ['rp4', 'rp3', 'rp6', 'AI-AO-4']]
        self.defend_zones = [['rp1', 'rp2', 'rp3', 'rp4']]
        self.support_zones = [['rp5', 'rp6', 'rp7', 'rp8']]
        self.prosecution_zones = [['rp9', 'rp10', 'rp11', 'rp12']]
        self.lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
        self.lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']
        self.lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04']
        self.lst_4 = ['F-16A #1', 'F-16A #2', 'F-16A #3', 'F-16A #4']
        self.lst_5 = ['E-2K #1']
        self.lst_6 = ['EC-130H #1']
        self.lst_7 = ['EC-130H #2']
        self.times = 15
        self.delta = 0.5  # 时间间隔1分钟
        self.delta_1 = 0.25
        self.offend_zone = ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4']
        self.asuw = {k: v for k, v in self.side.aircrafts.items()
                     if '停放' in v.strActiveUnitStatus
                     and (len(v.m_MultipleMissionGUIDs) == 0) and v.strName in self.lst_3 + self.lst_4}  # 剩余可用反舰空战飞机
        self.asup = {k: v for k, v in self.side.aircrafts.items()
                     if '停放' in v.strActiveUnitStatus
                     and (len(v.m_MultipleMissionGUIDs) == 0) and v.strName in self.lst_1 + self.lst_2}  # 剩余可用空战飞机
        self.support_unit = {k: v for k, v in self.side.aircrafts.items()
                     if '停放' in v.strActiveUnitStatus
                     and (len(v.m_MultipleMissionGUIDs) == 0) and v.strName in self.lst_5 + self.lst_6 + self.lst_7}  # 剩余可用支援飞机
        # self.target = {k: v for k, v in self.side.contacts.items() if v.m_ContactType == 2 and v.strName in ['航空母舰','护卫舰','驱逐舰']}
        self.target = {k: v for k, v in self.side.contacts.items() if (('航空母舰' in v.strName) | ('护卫舰' in v.strName) | ('驱逐舰' in v.strName))}
        self.time_zone_combine = list(
            itertools.product([x for x in range(self.times)], [y for y in range(len(self.defend_zones))]))

        # self._actions = list(
        #     chain.from_iterable([self._Action('donothing', self._ActionDoNothing, self._DoNothingIsValid),
        #                          self._Action('defensive', self._DefensiveAirMissionAction, self._PatrolMissionIsValid),
        #                          self._Action('offensive', self._OffensiveAirMissionAction, self._PatrolMissionIsValid),
        #                          self._Action('attack', self._AttackAntiSurfaceShipMissionAction,
        #                                       self._AttackMissionIsValid)]))
        self._actions = list(
            chain.from_iterable([self._Action('donothing', self._ActionDoNothing, self._DoNothingIsValid),
                                 self._Action('defensive', self._DefensiveAirMissionAction, self._PatrolMissionIsValid),
                                 self._Action('attack', self._AttackAntiSurfaceShipMissionAction,
                                              self._AttackMissionIsValid),
                                 self._Action('support', self._supportMission, self._supportMissionIsValid)]))
        self.action_space = MaskDiscrete(len(self._actions))
        self.zones()
    def zones(self):
        start_lat = 22.3166521609224
        start_lon = 121.148610750252
        end_lat = 20.8166611844987
        end_lon = 124.450782265488
        a = []
        k = 0
        side = self.scenario.get_side_by_name('蓝方')
        for i in np.linspace(end_lat, start_lat, 4):
            for j in np.linspace(start_lon, end_lon, 4):
                a.append([i, j])
                k += 1
                side.add_reference_point('ppp' + str(k), i, j)
        print(a)

        index_list = []
        for k in [0, 1, 2, 4, 5, 6, 8, 9, 10]:
            index_list.append([k, k + 1, k + 4, k + 5])
        print(index_list)
        b = []
        for m in index_list:
            c = []
            for n in m:
                c.append(a[n])
            b.append(c)
        print(b)
    def _Action(self, type, function, is_valid):
        if type == 'donothing':
            func_list = []
            func_list.append(Function(type=type, function=function(), is_valid=is_valid()))
            return func_list
        elif type == 'defensive':
            func_list = []
            for times, i in self.time_zone_combine:
                missionName = 'defensive-' + str(uuid.uuid1())
                # key = random.choice(list(self.asup.keys()))
                # missionUnit = {key: self.asup[key]}
                zone = self.defend_zones[i]
                prosecution_zone = self.prosecution_zones[i]
                func_list.append(Function(type=type, function=function(missionName, times, zone, prosecution_zone), is_valid=is_valid()))
            return func_list
        elif type == 'attack':
            func_list = []
            # for times in range(5, self.times * 2):
            for times in range(2, 27):
                missionName = 'attack-' + str(uuid.uuid1())
                # key = random.choice(list(self.asuw.keys()))
                # missionUnit = {key: self.asuw[key]}
                func_list.append(
                    Function(type=type, function=function(missionName, times, self.target), is_valid=is_valid()))
            return func_list
        elif type == 'support':
            func_list = []
            for times, i in self.time_zone_combine:
                missionName = 'support-' + str(uuid.uuid1())
                # key = random.choice(list(self.asup.keys()))
                # missionUnit = {key: self.asup[key]}
                zone = self.support_zones[i]
                func_list.append(Function(type=type, function=function(missionName, times, zone), is_valid=is_valid()))
            return func_list
        else:
            raise NotImplementedError

    def _get_valid_action_mask(self):
        ids = [i for i, action in enumerate(self._actions) if action.is_valid()]
        mask = np.zeros(self.action_space.n)
        mask[ids] = 1
        return mask

    def _update(self, scenario):
        self.scenario = scenario
        self.side = self.scenario.get_side_by_name(self.sideName)
        # self.asuw = {k: v for k, v in self.side.aircrafts.items()
        #              if int(re.sub('\D', '', v.strLoadoutDBGUID)) == 3004
        #              and (len(v.m_MultipleMissionGUIDs) == 0)}  # 剩余可用反舰空战飞机
        # self.asuw = {k: v for k, v in self.side.aircrafts.items() if v.strName in self.lst_3 or v.strName in self.lst_4
        #              or v.strName in self.lst_5}
        self.asuw = {k: v for k, v in self.side.aircrafts.items()
                     if '停放' in v.strActiveUnitStatus
                     and (len(v.m_MultipleMissionGUIDs) == 0) and v.strName in self.lst_3 + self.lst_4}  # 剩余可用反舰空战飞机

        # self.asup = {k: v for k, v in self.side.aircrafts.items()
        #              if int(re.sub('\D', '', v.strLoadoutDBGUID)) == 19361
        #              and (len(v.m_MultipleMissionGUIDs) == 0)}  # 剩余可用空战飞机
        # self.asup = {k: v for k, v in self.side.aircrafts.items() if v.strName in self.lst_1}
        self.asup = {k: v for k, v in self.side.aircrafts.items()
                     if '停放' in v.strActiveUnitStatus
                     and (len(v.m_MultipleMissionGUIDs) == 0) and v.strName in self.lst_1 + self.lst_2 }  # 剩余可用空战飞机
        self.support_unit = {k: v for k, v in self.side.aircrafts.items() if v.strName in self.lst_5 + self.lst_6 + self.lst_7}
        # self.target = {k: v for k, v in self.side.contacts.items() if v.m_ContactType == 2 and v.strName in ['航空母舰','护卫舰','驱逐舰']}
        self.target = {k: v for k, v in self.side.contacts.items() if
                       (('航空母舰' in v.strName) | ('护卫舰' in v.strName) | ('驱逐舰' in v.strName))}
        self.m_StartTime = self.scenario.m_StartTime  # 想定开始时间
        self.m_Time = self.scenario.m_Time  # 想定当前时间
        # self._create_or_update_battle_zone()
        # self._CreateOrUpdateOffensivePatrolZone()
        self._CreateOrUpdateDenfensivePatrolZone()
        self._CreatOrUpdateSupportZone()
        self._CreatOrUpdatePresecutionZone()
        self.evade_ship_for_antiship()
        doctrine = self.side.get_doctrine()

        doctrine.set_fuel_state_for_aircraft('0')
        self.edit_weapon_doctrine(doctrine)
        self.edit_anti_ship_weapon_doctrine(doctrine)
        doctrine.set_fuel_state_for_air_group('0')
        # 设置单架飞机的武器状态
        doctrine.set_weapon_state_for_aircraft('2002')
        doctrine.set_weapon_state_for_air_group('0')
    def _assign_available_unit(self, action):
        if self._actions[action].type == 'donothing':
            mission_unit = {}
            pass
        elif self._actions[action].type == 'defensive':
            if len(self.asup) == 0:
                print('action: ', action, '未分配单元')
                return None
            key = random.choice(list(self.asup.keys()))
            mission_unit = {key: self.asup[key]}
        elif self._actions[action].type == 'attack':
            if len(self.asuw) == 0:
                print('action: ', action, '未分配单元')
                return None
            key = random.choice(list(self.asuw.keys()))
            mission_unit = {key: self.asuw[key]}
        elif self._actions[action].type == 'support':
            if len(self.support_unit) == 0:
                print('action: ', action, '未分配单元')
                return None
            key = random.choice(list(self.support_unit.keys()))
            mission_unit = {key: self.support_unit[key]}
        else:
            raise NotImplementedError
        for k, v in mission_unit.items():
            # print('k:', k, 'v:', v)
            # pdb.set_trace()
            print('action: ', action, 'unit_name: ', v.strName)
        return mission_unit

    def step(self, action):
        mission_unit = self._assign_available_unit(action)
        if mission_unit != None:
            self._actions[action].function(mission_unit)
        print('action:', action)
        scenario = self._env.step()  # 墨子环境step，无用
        self._update(scenario)
        mask = self._get_valid_action_mask()
        done = self._is_done()
        return scenario, mask, done

    def reset(self):
        scenario = self._env.reset(self.sideName)
        self._update(scenario)
        mask = self._get_valid_action_mask()
        return scenario, mask

    def _is_done(self):
        # pdb.set_trace()
        # duration = int(self.time[0]) * 86400 + int(self.time[1]) * 3600 + int(self.time[2]) * 60
        # if self.m_StartTime + duration <= self.m_Time + 30:
        #     return True
        # else:
        #     pass
        # if len(self.side.contacts) == 0 or len(self.side.aircrafts) == 0:
        #     return True
        # else:
        #     return False

        # 对战平台
        response_dic = self.scenario.get_responses()
        for _, v in response_dic.items():
            if v.Type == 'EndOfDeduction':
                print('打印出标记：EndOfDeduction')
                if self._env.agent_key_event_file:
                    self._env.mozi_server.write_key_event_string_to_file('推演结束！')
                return True
        return False

    # 修改任务参数
    def _SetTaskParam(self, mission, kwargs):
        # kwargs = {'missionName': miss1, 'missionType': '空战巡逻', 'flightSize': 2, 'checkFlightSize': True, 'oneThirdRule': True,
        #           'chechOpa': False, 'checkWwr': True, 'startTime': '08/09/2020 00:00:00',
        #           'endTime': '08/09/2020 12:00:00', 'isActive': 'true', 'missionUnit': , 'targets': }
        kwargs_keys = kwargs.keys()
        # 设置编队规模
        if 'flightSize' in kwargs_keys:
            mission.set_flight_size(kwargs['flightSize'])
        # 检查编队规模
        if 'checkFlightSize' in kwargs_keys:
            mission.set_flight_size_check('false')  # True
        # 设置1/3规则
        if 'oneThirdRule' in kwargs_keys:
            mission.set_one_third_rule(kwargs['oneThirdRule'])
        # 是否对巡逻区外的探测目标进行分析
        if 'chechOpa' in kwargs_keys:
            mission.set_opa_check(str(kwargs['chechOpa']))
        # 是否对武器射程内探测目标进行分析
        if 'checkWwr' in kwargs_keys:
            mission.set_wwr_check(kwargs['checkWwr'])
        # 设置任务的开始和结束时间
        if 'startTime' in kwargs_keys:
            cmd_str = "ScenEdit_SetMission('" + self.sideName + "','" + kwargs['missionName'] + "',{starttime='" + \
                      kwargs['startTime'] + "'})"
            self.scenario.mozi_server.send_and_recv(cmd_str)
        # if 'endTime' in kwargs_keys:
        #     cmd_str = "ScenEdit_SetMission('" + self.sideName + "','" + kwargs['missionName'] + "',{endtime='" + kwargs[
        #         'endTime'] + "'})"
        #     self.scenario.mozi_server.send_and_recv(cmd_str)
        # 设置是否启动任务
        # if 'isActive' in kwargs_keys:
        #     lua = "ScenEdit_SetMission('%s','%s',{isactive='%s'})" % (self.sideName, kwargs['missionName'], kwargs['isActive'])
        #     self.scenario.mozi_server.send_and_recv(lua)
        if 'missionUnit' in kwargs_keys:
            mission.assign_units(kwargs['missionUnit'])

        if 'targets' in kwargs_keys:
            # mission.assign_targets(kwargs['targets'])
            # self.side.assign_target_to_mission(kwargs['targets'], mission.strName)
            doctrine_2 = mission.get_doctrine()
            for k, v in kwargs['targets'].items():
                print('name=',v.strName)
                mission.assign_unit_as_target(k)
                # if '护卫舰' in v.strName:
                #     geopoint_target = (v.dLatitude, v.dLongitude)
                #     for air in kwargs['missionUnit'].values():
                #         if '返回基地' in air.strActiveUnitStatus:
                #             continue
                #         doctrine = air.get_doctrine()
                #         doctrine.set_emcon_according_to_superiors('no')
                #         doctrine.set_em_control_status('Radar', 'Passive')
                #         self.evade_ship(geopoint_target, air, doctrine)
        if 'plan_way' in kwargs_keys:
            mission.add_plan_way_to_mission(0, kwargs['plan_way'])
            # mission.add_plan_way_to_mission(2, '航线1')
        if 'patrol_zone' in kwargs_keys:
            mission.set_patrol_zone(kwargs['patrol_zone'])
        if 'prosecution_zone' in kwargs_keys:
            mission.set_prosecution_zone(kwargs['prosecution_zone'])
    # 修改支援任务参数
    def _SetSupportTaskParam(self, mission, kwargs):
        # kwargs = {'missionName': miss1, 'missionType': '空战巡逻', 'flightSize': 2, 'checkFlightSize': True, 'oneThirdRule': True,
        #           'chechOpa': False, 'checkWwr': True, 'startTime': '08/09/2020 00:00:00',
        #           'endTime': '08/09/2020 12:00:00', 'isActive': 'true', 'missionUnit': , 'targets': }
        kwargs_keys = kwargs.keys()
        # 设置编队规模
        if 'flightSize' in kwargs_keys:
            mission.set_flight_size(kwargs['flightSize'])
        # 检查编队规模
        if 'checkFlightSize' in kwargs_keys:
            mission.set_flight_size_check('false')  # True
        # 设置1/3规则
        if 'oneThirdRule' in kwargs_keys:
            mission.set_one_third_rule(kwargs['oneThirdRule'])
        # 设置任务的开始和结束时间
        if 'startTime' in kwargs_keys:
            cmd_str = "ScenEdit_SetMission('" + self.sideName + "','" + kwargs['missionName'] + "',{starttime='" + \
                      kwargs['startTime'] + "'})"
            self.scenario.mozi_server.send_and_recv(cmd_str)
        if 'endTime' in kwargs_keys:
            cmd_str = "ScenEdit_SetMission('" + self.sideName + "','" + kwargs['missionName'] + "',{endtime='" + kwargs[
                'endTime'] + "'})"
            self.scenario.mozi_server.send_and_recv(cmd_str)
        # 设置是否启动任务
        # if 'isActive' in kwargs_keys:
        #     lua = "ScenEdit_SetMission('%s','%s',{isactive='%s'})" % (self.sideName, kwargs['missionName'], kwargs['isActive'])
        #     self.scenario.mozi_server.send_and_recv(lua)
        if 'missionUnit' in kwargs_keys:
            mission.assign_units(kwargs['missionUnit'])
            for air in kwargs['missionUnit'].values():
                if air.strName == 'E-2K #1':
                    doctrine = air.get_doctrine()
                    doctrine.set_em_control_status('Radar', 'Active')
                elif air.strName in ['EC-130H #1', 'EC-130H #2']:
                    doctrine = air.get_doctrine()
                    doctrine.set_em_control_status('OECM', 'Active')
    # 修改任务条令、电磁管控
    def _SetTaskDoctrineAndEMC(self, doctrine, kwargs):
        kwargs_keys = kwargs.keys()
        # 设置单架飞机返航的油料状态
        if 'fuelStateForAircraft' in kwargs_keys:
            doctrine.set_fuel_state_for_aircraft(kwargs['fuelStateForAircraft'])
            self.edit_weapon_doctrine(doctrine)
        if 'fuelStateForAirGroup' in kwargs_keys:
            doctrine.set_fuel_state_for_air_group(kwargs['fuelStateForAirGroup'])
        # 设置单架飞机的武器状态
        if 'weaponStateForAircraft' in kwargs_keys:
            doctrine.set_weapon_state_for_aircraft(kwargs['weaponStateForAircraft'])
        if 'weaponStateForAirGroup' in kwargs_keys:
            doctrine.set_weapon_state_for_air_group(kwargs['weaponStateForAirGroup'])

    # 修改对海打击任务条令、电磁管控
    def _SetTaskDoctrineAntiship(self, doctrine, kwargs):
        # 设置单架飞机返航的油料状态
        kwargs_keys = kwargs.keys()
        if 'fuelStateForAircraft' in kwargs_keys:
            doctrine.set_fuel_state_for_aircraft(kwargs['fuelStateForAircraft'])
            self.edit_anti_ship_weapon_doctrine(doctrine)
        if 'fuelStateForAirGroup' in kwargs_keys:
            doctrine.set_fuel_state_for_air_group(kwargs['fuelStateForAirGroup'])
        # 设置单架飞机的武器状态
        if 'weaponStateForAircraft' in kwargs_keys:
            doctrine.set_weapon_state_for_aircraft(kwargs['weaponStateForAircraft'])
        if 'weaponStateForAirGroup' in kwargs_keys:
            doctrine.set_weapon_state_for_air_group(kwargs['weaponStateForAirGroup'])
    def _PatrolMissionIsValid(self):
        def is_valid():
            if len(self.asup) == 0:
                return False
            else:
                return True

        return is_valid

    def _AttackMissionIsValid(self):
        def is_valid():
            if len(self.asuw) == 0:
                return False
            else:
                return True

        return is_valid

    def _supportMissionIsValid(self):
        def is_valid():
            if len(self.support_unit) == 0:
                return False
            else:
                return True
        return is_valid
    def _DoNothingIsValid(self):
        def is_valid():
            return True

        return is_valid

    def _ActionDoNothing(self):
        def act(mission_unit):
            pass

        return act

    # 防御性巡逻任务
    '''
    def step(self, action):
        mission_unit = self._assign_available_unit(action)
        if mission_unit != None:
            self._actions[action].function(mission_unit)
    这里面是对act(missionUnit)赋值
    '''
    def _DefensiveAirMissionAction(self, missionName, times, zone, prosecution_zone):
        def act(missionUnit):
            side = self.side
            # zone = ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4']
            patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == missionName]
            if len(patrolmssn) != 0:
                return False
            scen_time = '05/26/2021 11:00:00'
            mission_time = datetime.datetime.strptime(scen_time, '%m/%d/%Y %H:%M:%S') + datetime.timedelta(
                minutes=self.delta * times)
            DefensiveAirMiss = side.add_mission_patrol(missionName, 0, zone)  # 空战巡逻
            # DefensiveAirMiss = CPatrolMission('T+1_mode', self.scenario.mozi_server, self.scenario.situation)
            DefensiveAirMiss.strName = missionName
            taskParam = {'missionName': missionName, 'missionType': '空战巡逻', 'flightSize': 1, 'checkFlightSize': False,
                         'oneThirdRule': False, 'chechOpa': True, 'checkWwr': True,
                         'startTime': '%s' % str(mission_time),
                         'endTime': '05/26/2021 14:30:00', 'isActive': 'true', 'missionUnit': missionUnit,'patrol_zone': zone, 'prosecution_zone':prosecution_zone}
            self._SetTaskParam(DefensiveAirMiss, taskParam)
            print('missionName ', missionName, 'startTime', mission_time, '***', len(missionUnit))

            doctrine = DefensiveAirMiss.get_doctrine()
            doctrineParam = {'emc_radar': 'Passive', 'evadeAuto': 'true', 'ignorePlottedCourse': 'yes',
                             'targetsEngaging': 'true',
                             'ignoreEmcon': 'false', 'weaponControlAir': '0', 'weaponControlSurface': '0',
                             'fuelStateForAircraft': '0',
                             'fuelStateForAirGroup': '0', 'weaponStateForAircraft': '2002',
                             'weaponStateForAirGroup': '0'}
            # if doctrine is not None:
            #     self._SetTaskDoctrineAndEMC(doctrine, doctrineParam)

        return act


    def _supportMission(self, missionName, times, zone):
        def act(missionUnit):
            side = self.side
            # zone = ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4']
            patrolmssn = [v for _, v in side.supportmssns.items() if v.strName == missionName]
            if len(patrolmssn) != 0:
                return False
            scen_time = '05/26/2021 11:00:00'
            mission_time = datetime.datetime.strptime(scen_time, '%m/%d/%Y %H:%M:%S') + datetime.timedelta(
                minutes=self.delta * times)
            SupportMiss = side.add_mission_support(missionName, zone)  # 支援
            # DefensiveAirMiss = CPatrolMission('T+1_mode', self.scenario.mozi_server, self.scenario.situation)
            SupportMiss.strName = missionName
            taskParam = {'missionName': missionName, 'missionType': '支援任务', 'flightSize': 1, 'checkFlightSize': False,
                         'oneThirdRule': False, 'chechOpa': True, 'checkWwr': True,
                         'startTime': '%s' % str(mission_time),
                         'endTime': '05/26/2021 14:30:00', 'isActive': 'true', 'missionUnit': missionUnit}
            self._SetSupportTaskParam(SupportMiss, taskParam)
            print('missionName ', missionName, 'startTime', mission_time, '***', len(missionUnit))
        return act

    # 对海打击任务
    def _AttackAntiSurfaceShipMissionAction(self, missionName, times, target):
        def act(missionUnit):
            side = self.side
            strikemssn = [v for _, v in side.strikemssns.items() if v.strName == missionName]
            if len(strikemssn) != 0:
                return False

            _target = target
            if len(_target) == 0:
                _target = {k: v for k, v in self.side.contacts.items() if (('航空母舰' in v.strName) | ('护卫舰' in v.strName) | ('驱逐舰' in v.strName))}
            # for k, v in _target.items():
            #     # set_mark_contact设置目标对抗关系,H is 敌方
            #     side.set_mark_contact(k, 'U')
            target_1 = {k: v for k, v in _target.items() if ('护卫舰' in v.strName)}
            scen_time = '05/26/2021 12:00:00'
            mission_time = datetime.datetime.strptime(scen_time, '%m/%d/%Y %H:%M:%S') + datetime.timedelta(
                minutes=self.delta_1 * times)
            AntiSurface = side.add_mission_strike(missionName, 2)
            # AntiSurface = CStrikeMission('T+1_mode', self.scenario.mozi_server, self.scenario.situation)
            AntiSurface.strName = missionName
            taskParam = {'missionName': missionName, 'missionType': '对海打击', 'flightSize': 1, 'checkFlightSize': False,
                         'startTime': '%s' % str(mission_time),
                         'endTime': '05/26/2021 14:30:00', 'isActive': 'true', 'missionUnit': missionUnit,
                         'targets': target_1, 'plan_way': '航线2'}
            self._SetTaskParam(AntiSurface, taskParam)
            print('missionName ', missionName, 'startTime', mission_time, '***', len(missionUnit))
            doctrine = AntiSurface.get_doctrine()
            doctrineParam = {'emc_radar': 'Passive', 'evadeAuto': 'true', 'ignorePlottedCourse': 'yes',
                             'targetsEngaging': 'true',
                             'ignoreEmcon': 'false', 'weaponControlAir': '0', 'weaponControlSurface': '0',
                             'fuelStateForAircraft': '0',
                             'fuelStateForAirGroup': '3', 'weaponStateForAircraft': '2002',
                             'weaponStateForAirGroup': '3'}
            # if doctrine is not None:
            #     self._SetTaskDoctrineAntiship(doctrine, doctrineParam)

        return act


    # 生成或更新防御性巡逻区域
    def _CreateOrUpdateDenfensivePatrolZone(self):
        side = self.side
        zones = ['rp1', 'rp2', 'rp3', 'rp4']
        rps = [k for k, v in side.referencepnts.items() if v.strName in zones]
        # rps = [v.strName for k, v in side.referencepnts.items() if v.strName in zones]
        point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
                   (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
        if len(rps) != 4:
            # 巡逻任务1
            side.add_reference_point('rp1', point_1[0][0], point_1[0][1])
            side.add_reference_point('rp2', point_1[1][0], point_1[1][1])
            side.add_reference_point('rp3', point_1[2][0], point_1[2][1])
            side.add_reference_point('rp4', point_1[3][0], point_1[3][1])

            # 巡逻任务1
            cmd1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp1', point_1[0][0], point_1[0][1])
            self.scenario.mozi_server.send_and_recv(cmd1)
            cmd2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp2', point_1[1][0], point_1[1][1])
            self.scenario.mozi_server.send_and_recv(cmd2)
            cmd3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp3', point_1[2][0], point_1[2][1])
            self.scenario.mozi_server.send_and_recv(cmd3)
            cmd4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp4', point_1[3][0], point_1[3][1])
            self.scenario.mozi_server.send_and_recv(cmd4)

    # 生成或更新支援巡逻区域
    def _CreatOrUpdateSupportZone(self):
        side = self.side
        zones = ['rp5', 'rp6', 'rp7', 'rp8']
        rps = [k for k, v in side.referencepnts.items() if v.strName in zones]
        # rps = [v.strName for k, v in side.referencepnts.items() if v.strName in zones]
        # point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
        #            (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
        point_1 = [(22.4098475117646, 122.186072181501), (22.418764139488, 122.367143273071),
                   (22.233752742808, 122.386191481229), (22.2336414046035, 122.186317353378)]
        if len(rps) != 4:
            # 巡逻任务1
            side.add_reference_point('rp5', point_1[0][0], point_1[0][1])
            side.add_reference_point('rp6', point_1[1][0], point_1[1][1])
            side.add_reference_point('rp7', point_1[2][0], point_1[2][1])
            side.add_reference_point('rp8', point_1[3][0], point_1[3][1])

            # 巡逻任务1
            cmd1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp5', point_1[0][0], point_1[0][1])
            self.scenario.mozi_server.send_and_recv(cmd1)
            cmd2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp6', point_1[1][0], point_1[1][1])
            self.scenario.mozi_server.send_and_recv(cmd2)
            cmd3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp7', point_1[2][0], point_1[2][1])
            self.scenario.mozi_server.send_and_recv(cmd3)
            cmd4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp8', point_1[3][0], point_1[3][1])
            self.scenario.mozi_server.send_and_recv(cmd4)
    # 创建警戒区
    def _CreatOrUpdatePresecutionZone(self):
        side = self.side
        zones = ['rp9', 'rp10', 'rp11', 'rp12']
        rps = [k for k, v in side.referencepnts.items() if v.strName in zones]
        # rps = [v.strName for k, v in side.referencepnts.items() if v.strName in zones]
        # point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
        #            (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
        # point_1 = [(22.4098475117646, 122.186072181501), (22.418764139488, 122.367143273071),
        #            (22.233752742808, 122.386191481229), (22.2336414046035, 122.186317353378)]
        point_1 = [(22.1593596923231, 121.147008976371), (22.5329177785997, 123.746663413981),
                   (21.705618145078, 123.70585754102), (21.2291643151066, 121.162975576448)]
        if len(rps) != 4:
            # 巡逻任务1
            side.add_reference_point('rp9', point_1[0][0], point_1[0][1])
            side.add_reference_point('rp10', point_1[1][0], point_1[1][1])
            side.add_reference_point('rp11', point_1[2][0], point_1[2][1])
            side.add_reference_point('rp12', point_1[3][0], point_1[3][1])

            # 巡逻任务1
            cmd1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp9', point_1[0][0], point_1[0][1])
            self.scenario.mozi_server.send_and_recv(cmd1)
            cmd2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp10', point_1[1][0], point_1[1][1])
            self.scenario.mozi_server.send_and_recv(cmd2)
            cmd3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp11', point_1[2][0], point_1[2][1])
            self.scenario.mozi_server.send_and_recv(cmd3)
            cmd4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                self.sideName, 'rp12', point_1[3][0], point_1[3][1])
            self.scenario.mozi_server.send_and_recv(cmd4)

    def evade_ship(self, geopoint_target, air, mission_doctrine):
        geopoint_air = (air.dLatitude, air.dLongitude)
        if geopoint_target:
            dis = get_horizontal_distance(geopoint_air, geopoint_target)
            # print('dis=',dis)
            # latitude = '19.4047912416051', longitude = '125.261903097423'
            # latitude = '19.2371461750409', longitude = '125.24901570037'
            if dis < 150:
                mission_doctrine.ignore_plotted_course('yes')
                genpoint_away = (geopoint_target[0] - 0.17, geopoint_target[1] - 0.02)
                air.plot_course([genpoint_away])
    def evade_ship_for_antiship(self):
        side = self.side
        asuw_1 = {k: v for k, v in self.side.aircrafts.items() if v.strName in self.lst_3 or v.strName in self.lst_4}
        target_huwei = [v for k, v in side.contacts.items() if '护卫舰' in v.strName]
        mssnSitu = side.strikemssns
        strkmssn = [v for v in mssnSitu.values() if 'attack' in v.strName]
        if len(strkmssn) != 0:
            for strike in strkmssn:
                doctrine_2 = strike.get_doctrine()
                # missionUnits = strike.m_AssignedUnits.split('@')
                # missionUnits_fight = [asuw_1[unit] for unit in missionUnits]
                if target_huwei:
                    geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
                    for air in asuw_1.values():
                        if '返回基地' in air.strActiveUnitStatus:
                            continue
                        doctrine = air.get_doctrine()
                        doctrine.set_emcon_according_to_superiors('no')
                        doctrine.set_em_control_status('Radar', 'Passive')
                        self.evade_ship(geopoint_target, air, doctrine_2)

    # 用于巡逻任务中编辑武器条令,空空弹武器条例
    def edit_weapon_doctrine(self, doctrine):
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
    def edit_anti_ship_weapon_doctrine(self, doctrine):
        # AGM - 84L: 816
        doctrine.set_weapon_release_authority('816', '2999', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3101', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3102', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3103', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3000', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3104', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3105', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3106', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3107', '2', '1', '60', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3108', '2', '1', '60', 'none', 'false')