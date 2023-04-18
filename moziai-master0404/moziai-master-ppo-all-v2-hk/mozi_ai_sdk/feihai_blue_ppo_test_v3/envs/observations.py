# 时间 ： 2020/8/31 21:10
# 作者 ： Dixit
# 文件 ： observations.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司

import numpy as np
import re
from gym import spaces
from functools import reduce
from mozi_ai_sdk.dppo.utils.utils import *

# 单元类型、数量、在区域内在空的数量、空闲的数量、被击落、击沉的数量
# 在空所有飞机的武器类型和数量、消耗所有武器类型与数量
# 当前推演进度
# 任务类型、任务数量
# 探测信息（飞机、驱逐舰、航母、武器挂架）
# 这个文件夹中主要是_features -> _generate_features
# strLoadoutDBGUID 这个字段已经没有了
# class Features(gym.Wrapper):
class Features(object):
    def __init__(self, env, scenario, sideName):
        self.sideName = sideName
        self.side = scenario.get_side_by_name(self.sideName)
        self._env = env
        # self.reward = float(self.side.iTotalScore) / 4067
        self.reward = float(self.side.iTotalScore) / 1344
        self.mozi_server = scenario.mozi_server
        self.ships = self.side.ships
        self.aircrafts = self.side.aircrafts
        self.contacts = self.side.contacts
        # asuw = 反舰 - 空战飞机
        self.asuw = 12
        # asup = 空战飞机
        self.asup = 6
        # self.destroyer = 1
        # ec 干扰机
        self.ec = 2
        # self.aircarrier = 1
        # e2k = 预警机
        self.e2k = 1
        self.toll = 384
        self.air2air_missile = 48
        self.antiship_missile = 24
        self.lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
        self.lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']
        self.lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04']
        self.lst_4 = ['F-16A #1', 'F-16A #2', 'F-16A #3', 'F-16A #4']
        self.lst_5 = ['E-2K #1']
        self.lst_6 = ['EC-130H #1']
        self.lst_7 = ['EC-130H #2']
        # self.airdefense_missile = 80
        # self.zones = {'saw_zone': ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4'],
        #               'zone_1': ['AI-AO-1', 'rp2', 'rp3', 'rp4'],
        #               'zone_2': ['rp2', 'AI-AO-2', 'rp5', 'rp3'],
        #               'zone_3': ['rp3', 'rp5', 'AI-AO-3', 'rp6'],
        #               'zone_4': ['rp4', 'rp3', 'rp6', 'AI-AO-4']}
        # self.zones = {'zone_1': ['rp1', 'rp2', 'rp3', 'rp4']}
        self.zones = {'zone_1': ['RP-3676', 'RP-3677', 'RP-3678', 'RP-3679']}
        self.combact_units_type = {'asuw': '0001', 'asup': '0010', 'ec': '0100', 'e2k': '1000'}
        # self.weapons_type = {'toll': '001', 'air2air_missile': '010', 'antiship_missile': '100'}
        self.weapons_type = {'toll': '0001', 'air2air_missile': '0010', 'antiship_missile': '0100',
                             'airdefense_missile': '1000'}
        self.contacts_type = {'missile': '001', 'aircraft': '010', 'ship': '100'}
        self.top_category = {'unit_type': '001', 'weapon_type': '010', 'contact_type': '100'}
        self.second_category = {'idle_unit_type': self.top_category['unit_type']+'001',
                                'loss_unit_type': self.top_category['unit_type']+'010',
                                'busy_unit_type': self.top_category['unit_type']+'100',
                                'consumed_weapon_type': self.top_category['weapon_type']+'01',
                                'surplus_weapon_type': self.top_category['weapon_type']+'10',
                                'hostile_in_zone_1': self.top_category['contact_type'] + '0001'}
        self.third_category = {'zone_1': self.second_category['busy_unit_type']+'00010'}
        self.stat_type = {
            # 空闲的单元类型stat_self_idle_unit_type
            'self_idle_asuw': self.second_category['idle_unit_type']+self.combact_units_type['asuw'],
            'self_idle_asup': self.second_category['idle_unit_type']+self.combact_units_type['asup'],
            'self_idle_ec': self.second_category['idle_unit_type']+self.combact_units_type['ec'],
            'self_idle_e2k': self.second_category['idle_unit_type']+self.combact_units_type['e2k'],
            # 损失的单元类型stat_self_loss_unit_type
            'self_loss_asuw': self.second_category['loss_unit_type']+self.combact_units_type['asuw'],
            'self_loss_asup': self.second_category['loss_unit_type']+self.combact_units_type['asup'],
            'self_loss_ec': self.second_category['loss_unit_type']+self.combact_units_type['ec'],
            'self_loss_e2k': self.second_category['loss_unit_type']+self.combact_units_type['e2k'],
            # 任务中的单元类型stat_self_busy_unit_type
            'self_busy_asuw': self.second_category['busy_unit_type'] + self.combact_units_type['asuw'],
            'self_busy_asup': self.second_category['busy_unit_type'] + self.combact_units_type['asup'],
            'self_busy_ec': self.second_category['busy_unit_type'] + self.combact_units_type['ec'],
            'self_busy_e2k': self.second_category['busy_unit_type'] + self.combact_units_type['e2k'],
            # 在区域saw_zone中的单元类型stat_self_saw_zone_unit_type
            # 在区域zone_1中的单元类型stat_self_zone_1_unit_type
            'self_zone_1_asuw': self.third_category['zone_1'] + self.combact_units_type['asuw'],
            'self_zone_1_asup': self.third_category['zone_1'] + self.combact_units_type['asup'],
            'self_zone_1_ec': self.third_category['zone_1'] + self.combact_units_type['ec'],
            'self_zone_1_e2k': self.third_category['zone_1'] + self.combact_units_type['e2k'],
            # 在区域zone_2中的单元类型stat_self_zone_2_unit_type
            # 在区域zone_3中的单元类型stat_self_zone_3_unit_type
            # 在区域zone_4中的单元类型stat_self_zone_4_unit_type
            # 消耗的武器类型stat_self_consumed_weapon_type
            'self_consumed_toll': self.second_category['consumed_weapon_type'] + self.weapons_type['toll'],
            'self_consumed_air2airmissile': self.second_category['consumed_weapon_type'] + self.weapons_type['air2air_missile'],
            'self_consumed_antishipmissile': self.second_category['consumed_weapon_type'] + self.weapons_type['antiship_missile'],
            'self_consumed_airdefensemissile': self.second_category['consumed_weapon_type'] + self.weapons_type[
                'airdefense_missile'],
            # 任务中所有单元剩余武器类型stat_self_surplus_weapon_type
            'self_surplus_toll': self.second_category['surplus_weapon_type'] + self.weapons_type['toll'],
            'self_surplus_air2airmissile': self.second_category['surplus_weapon_type'] + self.weapons_type['air2air_missile'],
            'self_surplus_antishipmissile': self.second_category['surplus_weapon_type'] + self.weapons_type['antiship_missile'],
            'self_surplus_airdefensemissile': self.second_category['surplus_weapon_type'] + self.weapons_type[
                'airdefense_missile'],
            # 探测到的敌方单元类型stat_hostile_unit_type
            # 'hostile_unknown': self.top_category['contact_type']+self.contacts_type['unknown'],
            'hostile_missile': self.top_category['contact_type'] + self.contacts_type['missile'],
            'hostile_aircraft': self.top_category['contact_type'] + self.contacts_type['aircraft'],
            'hostile_ship': self.top_category['contact_type'] + self.contacts_type['ship'],
            # 在区域zone_1中的敌方单元类型stat_hostile_zone_1_unit_type
            # 'hostile_zone_1_unknown': self.second_category['hostile_in_zone_1']+self.contacts_type['unknown'],
            'hostile_zone_1_missile': self.second_category['hostile_in_zone_1'] + self.contacts_type['missile'],
            'hostile_zone_1_aircraft': self.second_category['hostile_in_zone_1'] + self.contacts_type['aircraft'],
            'hostile_zone_1_ship': self.second_category['hostile_in_zone_1'] + self.contacts_type['ship'],
            # 在区域zone_2中的敌方单元类型stat_hostile_zone_2_unit_type
            # 'hostile_zone_2_unknown': self.second_category['hostile_in_zone_2'] + self.contacts_type['unknown'],
            # 在区域zone_3中的敌方单元类型stat_hostile_zone_3_unit_type
            # 'hostile_zone_3_unknown': self.second_category['hostile_in_zone_3'] + self.contacts_type['unknown'],
            # 在区域zone_4中的敌方单元类型stat_hostile_zone_4_unit_type
            # 'hostile_zone_4_unknown': self.second_category['hostile_in_zone_4'] + self.contacts_type['unknown'],
            }
        n_dims = reduce(lambda x, y: x+len(list(y)), list(self.stat_type.values()), 0) + len(self.stat_type)*1
        n_dims = 338
        # print('n_dims=',n_dims)
        self.action_space = self._env.action_space
        # self.observation_space = spaces.Tuple([spaces.Box(0.0, float('inf'), [n_dims], dtype=np.float32),
        #                                        spaces.Box(0.0, 1.0, [self._env.action_space.n], dtype=np.float32)])
        self.observation_space = spaces.Tuple([spaces.Box(0.0, float('inf'), [n_dims], dtype=np.float32),
                                               spaces.Box(0.0, 1.0, [self._env.action_space.n], dtype=np.float32)])

    def _update(self, scenario):
        self.side = scenario.get_side_by_name(self.sideName)
        # self.reward = float(self.side.iTotalScore) / 4067
        self.reward = float(self.side.iTotalScore) / 1344
        self.mozi_server = scenario.mozi_server
        self.ships = self.side.ships
        self.aircrafts = self.side.aircrafts
        self.contacts = self.side.contacts

    def step(self, action):
        # pdb.set_trace()
        scenario, mask, done = self._env.step(action)
        self._update(scenario) # 无用
        reward = self.reward
        obs = self._features()
        info = {}
        return (obs, mask), reward, done, info

    def reset(self):
        scenario, mask = self._env.reset()
        self._update(scenario)
        obs = self._features()
        # return (obs, mask)
        return obs

    def _features(self):
        # 空闲的单元类型stat_self_idle_unit_type
        feat_self_idle_unit = self._generate_features('stat_self_idle_unit_type', 'self_idle_asuw', 'self_idle_asup',
                                                            'self_idle_ec', 'self_idle_e2k')
        # 损失的单元类型stat_self_loss_unit_type
        feat_self_loss_unit = self._generate_features('stat_self_loss_unit_type', 'self_loss_asuw', 'self_loss_asup',
                                                            'self_loss_ec', 'self_loss_e2k')
        # 任务中的单元类型stat_self_busy_unit_type
        feat_self_busy_unit = self._generate_features('stat_self_busy_unit_type',
                                                      'self_busy_asuw', 'self_busy_asup',
                                                       'self_busy_ec', 'self_busy_e2k')
        # 在区域saw_zone中的单元类型stat_self_saw_zone_unit_type
        # 在区域zone_1中的单元类型stat_self_zone_1_unit_type
        feat_self_zone_1_unit = self._generate_features('stat_self_zone_1_unit_type',
                                                      'self_zone_1_asuw', 'self_zone_1_asup',
                                                       'self_zone_1_ec', 'self_zone_1_e2k')
        # 在区域zone_2中的单元类型stat_self_zone_2_unit_type
        # 在区域zone_3中的单元类型stat_self_zone_3_unit_type

        # 在区域zone_4中的单元类型stat_self_zone_4_unit_type

        # 消耗的武器类型stat_self_consumed_weapon_type
        feat_self_consumed_weapon = self._generate_features('stat_self_consumed_weapon_type',
                                                        'self_consumed_toll', 'self_consumed_air2airmissile',
                                                         'self_consumed_antishipmissile','self_consumed_airdefensemissile')
        # 任务中所有单元剩余武器类型stat_self_surplus_weapon_type
        feat_self_surplus_weapon = self._generate_features('stat_self_surplus_weapon_type',
                                                            'self_surplus_toll', 'self_surplus_air2airmissile',
                                                             'self_surplus_antishipmissile', 'self_surplus_airdefensemissile')
        # 探测到的敌方单元类型stat_hostile_unit_type
        feat_hostile_unit = self._generate_features('stat_hostile_unit_type', 'hostile_unknown', 'hostile_missile',
                                                                               'hostile_aircraft', 'hostile_ship')
        # 在区域zone_1中的敌方单元类型stat_hostile_zone_1_unit_type
        feat_hostile_zone_1_unit = self._generate_features('stat_hostile_zone_1_unit_type',
                                                           'hostile_zone_1_unknown', 'hostile_zone_1_missile',
                                                            'hostile_zone_1_aircraft', 'hostile_zone_1_ship')
        # 在区域zone_2中的敌方单元类型stat_hostile_zone_2_unit_type

        # 在区域zone_3中的敌方单元类型stat_hostile_zone_3_unit_type

        # 在区域zone_4中的敌方单元类型stat_hostile_zone_4_unit_type


        features = np.concatenate([feat_self_idle_unit,
                                   feat_self_loss_unit,
                                   feat_self_busy_unit,
                                   feat_self_zone_1_unit,
                                   feat_self_consumed_weapon,
                                   feat_self_surplus_weapon,
                                   feat_hostile_unit,
                                   feat_hostile_zone_1_unit,
                                   ])
        # print('features--shape=====',features.shape)
        return features

    @property
    def num_dims(self):
        pass

    def _generate_features(self, feat_type, *args):
        if len(args) != 4:
            raise ValueError
        if feat_type == 'stat_self_idle_unit_type':
            feat_self_idle_unit = np.array([])
            for key in ['self_idle_asuw', 'self_idle_asup', 'self_idle_ec', 'self_idle_e2k']:
                value = [int(i) for i in list(self.stat_type[key])]
                unit_type = key[key.rfind('_')+1:]
                num = self._get_self_idle_units(unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_idle_unit = np.concatenate((feat_self_idle_unit, value), axis=0)
            return feat_self_idle_unit
        elif feat_type == 'stat_self_loss_unit_type':
            feat_self_loss_unit = np.array([])
            for key in ['self_loss_asuw', 'self_loss_asup', 'self_loss_ec', 'self_loss_e2k']:
                value = [int(i) for i in list(self.stat_type[key])]
                unit_type = key[key.rfind('_') + 1:]
                num = self._get_self_loss_units(unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_loss_unit = np.concatenate((feat_self_loss_unit, value), axis=0)
            return feat_self_loss_unit
        elif feat_type == 'stat_self_busy_unit_type':
            feat_self_busy_unit = np.array([])
            for key in ['self_busy_asuw', 'self_busy_asup', 'self_busy_ec', 'self_busy_e2k']:
                value = [int(i) for i in list(self.stat_type[key])]
                unit_type = key[key.rfind('_') + 1:]
                num = self._get_self_busy_units(unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_busy_unit = np.concatenate((feat_self_busy_unit, value), axis=0)
            return feat_self_busy_unit
        elif feat_type == 'stat_self_zone_1_unit_type':
            feat_self_zone_1_unit = np.array([])
            for key in ['self_zone_1_asuw', 'self_zone_1_asup', 'self_zone_1_ec', 'self_zone_1_e2k']:
                value = [int(i) for i in list(self.stat_type[key])]
                unit_type = key[key.rfind('_') + 1:]
                num = self._get_zone_self_units('zone_1', unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_zone_1_unit = np.concatenate((feat_self_zone_1_unit, value), axis=0)
            return feat_self_zone_1_unit

        elif feat_type == 'stat_self_consumed_weapon_type':
            feat_self_consumed_weapon = np.array([])
            for key in ['self_consumed_toll', 'self_consumed_air2airmissile', 'self_consumed_antishipmissile']:
                value = [int(i) for i in list(self.stat_type[key])]
                weapon_type = key[key.rfind('_') + 1:]
                num = self._get_self_consumed_weapon(weapon_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_consumed_weapon = np.concatenate((feat_self_consumed_weapon, value), axis=0)
            return feat_self_consumed_weapon
        elif feat_type == 'stat_self_surplus_weapon_type':
            feat_self_surplus_weapon = np.array([])
            for key in ['self_surplus_toll', 'self_surplus_air2airmissile', 'self_surplus_antishipmissile']:
                value = [int(i) for i in list(self.stat_type[key])]
                weapon_type = key[key.rfind('_') + 1:]
                num = self._get_self_surplus_weapon(weapon_type)
                scaled_num = num / 600
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_self_surplus_weapon = np.concatenate((feat_self_surplus_weapon, value), axis=0)
            return feat_self_surplus_weapon
        elif feat_type == 'stat_hostile_unit_type':
            feat_hostile_unit = np.array([])
            for key in ['hostile_missile', 'hostile_aircraft', 'hostile_ship']:
                value = [int(i) for i in list(self.stat_type[key])]
                h_unit_type = key[key.rfind('_')+1:]
                num = self._get_hostile_units(h_unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_hostile_unit = np.concatenate((feat_hostile_unit, value), axis=0)
            return feat_hostile_unit
        elif feat_type == 'stat_hostile_zone_1_unit_type':
            feat_hostile_zone_1_unit = np.array([])
            for key in ['hostile_zone_1_missile', 'hostile_zone_1_aircraft', 'hostile_zone_1_ship']:
                value = [int(i) for i in list(self.stat_type[key])]
                h_unit_type = key[key.rfind('_') + 1:]
                num = self._get_zone_hostile_units('zone_1', h_unit_type)
                scaled_num = num / 16
                value.append(scaled_num)
                log_num = np.log10(scaled_num + 1)
                value.append(log_num)
                feat_hostile_zone_1_unit = np.concatenate((feat_hostile_zone_1_unit, value), axis=0)
            return feat_hostile_zone_1_unit
        else:
            raise TypeError

        return []

    def _get_self_idle_units(self, unit_type):
        """
        :param unit_type: 'asuw'、'asup'、'ec'、'e2k'
        # m_MultipleMissionGUIDs 单元所属多个任务guid拼接
        # strAirOpsConditionString 获取当前行动状态  0：空中,19：正在执行超视距攻击任务,20：超视距攻击往复运动
        # 21：近距空中格斗

        :return:
        """
        if unit_type == 'asuw':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_2 + self.lst_3 + self.lst_4:
                    if len(v.m_MultipleMissionGUIDs) == 0 or v.strAirOpsConditionString not in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'asup':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_1:
                    if len(v.m_MultipleMissionGUIDs) == 0 or v.strAirOpsConditionString not in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'ec':  # 电子干扰机
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_6 + self.lst_7:
                    if len(v.m_MultipleMissionGUIDs) == 0 or v.strAirOpsConditionString not in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'e2k':  # 预警机
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_5:
                    if len(v.m_MultipleMissionGUIDs) == 0 or v.strAirOpsConditionString not in [0, 19, 20, 21]:
                        num += 1
            return num
        else:
            raise TypeError

    def _get_self_busy_units(self, unit_type):
        """

        :param unit_type: 'asuw'、'asup'、'ec'、'e2k'
        :return:
        """
        if unit_type == 'asuw':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_2 + self.lst_3 + self.lst_4:
                    if len(v.m_MultipleMissionGUIDs) > 0 and v.strAirOpsConditionString in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'asup':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_1:
                    if len(v.m_MultipleMissionGUIDs) > 0 or v.strAirOpsConditionString in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'ec':  #
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_6 + self.lst_7:
                    if len(v.m_MultipleMissionGUIDs) > 0 or v.strAirOpsConditionString in [0, 19, 20, 21]:
                        num += 1
            return num
        elif unit_type == 'e2k':  #
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_5:
                    if len(v.m_MultipleMissionGUIDs) > 0 or v.strAirOpsConditionString in [0, 19, 20, 21]:
                        num += 1
            return num
        else:
            raise TypeError

    def _get_self_loss_units(self, unit_type):
        """

        :param unit_type: 'asuw'、'asup'、'ec'、'e2k'
        :return:
        """
        # self.side.m_Losses.split('@')
        if unit_type == 'asuw':
            surplus = 0
            for k, v in self.aircrafts.items():
                if v.m_LoadoutGuid == '': continue
                if v.strName in self.lst_2 + self.lst_3 + self.lst_4:
                    surplus += 1
            return 12 - surplus
        elif unit_type == 'asup':
            surplus = 0
            for k, v in self.aircrafts.items():
                if v.m_LoadoutGuid == '': continue
                if v.strName in self.lst_1:
                    surplus += 1
            return 6 - surplus
        elif unit_type == 'ec':  # 电子干扰机
            surplus = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_6 + self.lst_7:
                    surplus += 1
            return 2 - surplus
        elif unit_type == 'e2k':  # 预警机
            surplus = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_5:
                    surplus += 1
            return 1 - surplus
        else:
            raise TypeError

    def _get_zone_self_units(self, zone_type, unit_type):
        """

        :param zone_type: {'saw_zone': ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4'],
                      'zone_1': ['AI-AO-1', 'rp2', 'rp3', 'rp4'],
                      'zone_2': ['rp5', 'AI-AO-2', 'rp7', 'rp8'],
                      'zone_3': ['rp9', 'rp10', 'AI-AO-3', 'rp12'],
                      'zone_4': ['rp13', 'rp14', 'rp15', 'AI-AO-4']}
        :param unit_type: 'asuw'、'asup'、'ec'、'e2k'
        :return:
        """
        if zone_type not in ['zone_1']:
            raise TypeError

        zone_points = self.zones[zone_type]
        # print('zone_name=',[v.strName for k, v in self.side.referencepnts.items()])
        zone_ref = [{'name':v.strName ,'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in self.side.referencepnts.items()
                    if v.strName in zone_points]
        if len(zone_ref) == 0:
            return 0
        # print('zone_ref=',zone_ref)
        if unit_type == 'asuw':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_2 + self.lst_3 + self.lst_4:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        elif unit_type == 'asup':
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_1:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        elif unit_type == 'ec':  #
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_6 + self.lst_7:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        elif unit_type == 'e2k':  #
            num = 0
            for k, v in self.aircrafts.items():
                if v.strName in self.lst_5:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        else:
            raise TypeError

    def _get_self_consumed_weapon(self, weapon_type):
        """

        :param weapon_type: 'toll', 'air2air_missile', 'antiship_missile'
        :return:
        """
        expenditures = list(map(lambda x: x.split('$'), self.side.m_Expenditures.split('@')))
        if len(expenditures) == 0:
            return 0

        if weapon_type == 'toll':   # 诱饵弹 2051-通用红外干扰弹；564-通用箔条；3386-AN/ALE70
            num = 0
            for weapon in expenditures:
                if weapon[0] != '' and weapon[-1] != '':
                    if int(re.sub('\D', '', weapon[0])) in [564, 2051, 3386]:
                        num += int(weapon[-1])
            return num
        elif weapon_type == 'air2airmissile':  #   空空导弹  AIM-120C-7:718,AIM-9M:1384
            num = 0
            for weapon in expenditures:
                if weapon[0] != '' and weapon[-1] != '':
                    if int(re.sub('\D', '', weapon[0])) in [718, 1384]:
                        num += int(weapon[-1])
            return num
        elif weapon_type == 'antishipmissile':  #  反舰导弹  AGM-84L:816
            num = 0
            for weapon in expenditures:
                if weapon[0] != '' and weapon[-1] != '':
                    if int(re.sub('\D', '', weapon[0])) == 816:
                        num += int(weapon[-1])
            return num

        else:
            raise TypeError

    def _get_self_surplus_weapon(self, weapon_type):
        """
        弹药剩余数量
        :param weapon_type: 'toll', 'air2air_missile', 'antiship_missile'
        :return:
        """

        total_busy_units = self._get_self_total_busy_units()
        if len(total_busy_units) == 0:
            return 0
        if weapon_type == 'toll':   # 诱饵弹 2051-通用红外干扰弹；564-通用箔条；3386-AN/ALE70
            num = 0
            for unit in total_busy_units:
                weapon_list = self._get_unit_weapon(unit)
                for weapon in weapon_list:
                    if weapon[0] != '' and weapon[-1] != '':
                        if int(re.sub('\D', '', weapon[-1])) in [564, 2051, 3386]:
                            num += int(weapon[0])
            return num
        elif weapon_type == 'air2airmissile':  #   空空导弹  51-AIM120D;945-AIM9X
            num = 0
            for unit in total_busy_units:
                weapon_list = self._get_unit_weapon(unit)
                for weapon in weapon_list:
                    if weapon[0] != '' and weapon[-1] != '':
                        if int(re.sub('\D', '', weapon[-1])) in [718,1384]:
                            num += int(weapon[0])
            return num
        elif weapon_type == 'antishipmissile':  #  反舰导弹  826-AGM154C
            num = 0
            for unit in total_busy_units:
                weapon_list = self._get_unit_weapon(unit)
                for weapon in weapon_list:
                    if weapon[0] != '' and weapon[-1] != '':
                        if int(re.sub('\D', '', weapon[-1])) == 816:
                            num += int(weapon[0])
            return num
        else:
            raise TypeError

    def _get_self_total_busy_units(self):

        total_busy_units = []
        for k, v in self.aircrafts.items():
            if len(v.m_MultipleMissionGUIDs) > 0 and v.strAirOpsConditionString in [0, 19, 20, 21]:
                total_busy_units.append(v)
        return total_busy_units

    def _get_unit_weapon(self, unit):
        """

        :param unit: aircraft, ship
        :return:
        """
        weapon = list(map(lambda x: x.split('$'), unit.m_UnitWeapons.split('@')))
        weapon_list = list(map(lambda x, y: x+[y[-1]], list(map(lambda x: x[0].split('x '), weapon)), weapon))
        return weapon_list

    def _get_hostile_units(self, h_unit_type):
        """

        :param h_unit_type: unknown、missile、aircraft、ship
        0--空中目标
        1--导弹
        2--水面/地面

        :return:
        """
        contacts = self.contacts
        if h_unit_type == 'missile':  # m_ContactType = 1
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 1:
                    num += 1
            return num
        elif h_unit_type == 'aircraft': # m_ContactType = 0
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 0:
                    num += 1
            return num
        elif h_unit_type == 'ship':  # m_ContactType = 2
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 2:
                    num += 1
            return num
        else:
            raise TypeError

    def _get_zone_hostile_units(self, zone_type, h_unit_type):
        """

        :param zone_type: {'saw_zone': ['Offensive_rp_1', 'Offensive_rp_2', 'Offensive_rp_3', 'Offensive_rp_4'],
                      'zone_1': ['AI-AO-1', 'rp2', 'rp3', 'rp4'],
                      'zone_2': ['rp5', 'AI-AO-2', 'rp7', 'rp8'],
                      'zone_3': ['rp9', 'rp10', 'AI-AO-3', 'rp12'],
                      'zone_4': ['rp13', 'rp14', 'rp15', 'AI-AO-4']}
        :param h_unit_type: unknown、missile、aircraft、ship
        :return:
        """
        if zone_type not in ['zone_1']:
            raise TypeError

        zone_points = self.zones[zone_type]
        zone_ref = [{'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in self.side.referencepnts.items()
                    if v.strName in zone_points]

        contacts = self.contacts

        if h_unit_type == 'missile':
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 1:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        elif h_unit_type == 'aircraft':
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 0:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        elif h_unit_type == 'ship':
            num = 0
            for k, v in contacts.items():
                if v.m_ContactType == 2:
                    unit = {}
                    unit['latitude'] = v.dLatitude
                    unit['longitude'] = v.dLongitude
                    if zone_contain_unit(zone_ref, unit):
                        num += 1
            return num
        else:
            raise TypeError


