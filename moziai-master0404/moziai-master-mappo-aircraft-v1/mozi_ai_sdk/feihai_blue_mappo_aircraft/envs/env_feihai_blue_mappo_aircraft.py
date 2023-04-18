#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import numpy as np
import random
from math import cos
from math import radians

from mozi_utils import pylog
from mozi_utils.geo import get_point_with_point_bearing_distance
from mozi_utils.geo import get_degree
from mozi_utils.geo import get_two_point_distance
from mozi_ai_sdk.feihai_blue_ppo_v2.envs.utils import *
from mozi_ai_sdk.base_env import BaseEnvironment
from . import etc

'''
作者：
日期：
功能：
'''
class feihaiblue_mappo_aircraft(BaseEnvironment):
    """
    作者：
    日期：
    功能：构造函数
    参数：无
    返回：无
    """

    def __init__(self, IP, AIPort, agent_key_event_file, duration_interval, app_mode, synchronous=None,
                 simulate_compression=None, scenario_name=None, platform_mode=None, platform="windows"):
        super().__init__(IP, AIPort, platform, scenario_name, simulate_compression, duration_interval, synchronous,
                         app_mode, platform_mode)

        self.SERVER_PLAT = platform
        self.n = 5
        # self.observation_space =   # 状态空间维度
        # self.action_space = 9
        self.action_max = 8
        self.blue_unit_dict_list = None
        self.red_unit_dict = None
        self.observation = None
        self.red_side_name = "红方"
        self.blue_side_name = "蓝方"
        self.lst_1 = ['F-16A #7', 'F-16A #8']
        self.lst_2 = ['F-16A #9', 'F-16A #07']
        self.lst_3 = ['F-16A #08', 'F-16A #09']
        self.lst_4 = ['F-16A #5', 'F-16A #6']
        self.lst_5 = ['F-16A #05', 'F-16A #06']
        self.train_zones = None
    def init_train_zone(self):
        # 初始化9宫格
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        start_lat = 22.3166521609224
        start_lon = 121.148610750252
        end_lat = 20.8166611844987
        end_lon = 124.450782265488
        a = []
        k = 0
        for i in np.linspace(end_lat, start_lat, 4):
            for j in np.linspace(start_lon, end_lon, 4):
                a.append([i, j])
                k += 1
                self.blueside.add_reference_point('ppp' + str(k), i, j)

        index_list = []
        for k in [0, 1, 2, 4, 5, 6, 8, 9, 10]:
            index_list.append([k, k + 1, k + 4, k + 5])
        # print(index_list)
        b = []
        for m in index_list:
            c = []
            for n in m:
                c.append(a[n])
            b.append(c)
        self.train_zones = b
        return b

    # 先创建5个巡逻任务，让飞机动起来，然后利用学习出来的区域更新巡逻区
    def init_creat_patrol_mission(self):
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        flag = self.scenario.mozi_server.get_value_by_key(f'{self.blue_side_name}巡逻任务已创建')
        if flag == 'Yes':
            return False
        nine_zone = self.train_zones
        # 从9个区域里随机找一个，作为初始巡逻区
        patrol_zone_start = random.choice(nine_zone)
        point_list = self.create_patrol_zone(self.blueside, patrol_zone_start)
        i = 0
        point_prosecution_list = self.creat_prosecution_area(self.blueside)
        for point, jj_point in zip(point_list, point_prosecution_list):
            point_str = []
            ps_str = []
            for name in point:
                point_str.append(name.strName)
            for name in jj_point:
                ps_str.append(name.strName)
            # 新建巡逻区名字
            patrol_name = self.blue_side_name + 'xl' + str(i)
            patrolmssn = self.blueside.add_mission_patrol(patrol_name, 0, point_str)
            print('巡逻任务已创建')
            patrolmssn.set_one_third_rule('false')
            patrolmssn.set_patrol_zone(point_str)
            patrolmssn.set_prosecution_zone(ps_str)
            airs_xl1 = self.blue_unit_dict_list
            patrolmssn.assign_units(airs_xl1[i])
            patrolmssn.set_flight_size(2)
            patrolmssn.set_flight_size_check('false')
            patrolmssn.set_opa_check('true')
            patrolmssn.set_wwr_check('true')
            patrolmssn.set_emcon_usage('false')
            doctrine = self.blueside.get_doctrine()
            doctrine.set_fuel_state_for_aircraft('0')
            self.edit_weapon_doctrine(doctrine)
            doctrine.set_fuel_state_for_air_group('0')
            # 设置单架飞机的武器状态
            doctrine.set_weapon_state_for_aircraft('2002')
            doctrine.set_weapon_state_for_air_group('0')
            i += 1
        self.scenario.mozi_server.set_key_value(f'{self.blue_side_name}巡逻任务已创建', 'Yes')
    # 用随机选择的一个区域作为初始巡逻的巡逻区
    def create_patrol_zone(self, side, point_1):
        point_list = []
        rp1 = side.add_reference_point(self.blue_side_name + 'xl_point1', point_1[0][0], point_1[0][1])
        rp2 = side.add_reference_point(self.blue_side_name + 'xl_point2', point_1[1][0], point_1[1][1])
        rp3 = side.add_reference_point(self.blue_side_name + 'xl_point3', point_1[3][0], point_1[3][1])
        rp4 = side.add_reference_point(self.blue_side_name + 'xl_point4', point_1[2][0], point_1[2][1])
        point_list.append([rp1, rp2, rp3, rp4])
        rp5 = side.add_reference_point(self.blue_side_name + 'xl_point5', point_1[0][0], point_1[0][1])
        rp6 = side.add_reference_point(self.blue_side_name + 'xl_point6', point_1[1][0], point_1[1][1])
        rp7 = side.add_reference_point(self.blue_side_name + 'xl_point7', point_1[3][0], point_1[3][1])
        rp8 = side.add_reference_point(self.blue_side_name + 'xl_point8', point_1[2][0], point_1[2][1])
        point_list.append([rp5, rp6, rp7, rp8])
        rp9 = side.add_reference_point(self.blue_side_name + 'xl_point9', point_1[0][0], point_1[0][1])
        rp10 = side.add_reference_point(self.blue_side_name + 'xl_point10', point_1[1][0], point_1[1][1])
        rp11 = side.add_reference_point(self.blue_side_name + 'xl_point11', point_1[3][0], point_1[3][1])
        rp12 = side.add_reference_point(self.blue_side_name + 'xl_point12', point_1[2][0], point_1[2][1])
        point_list.append([rp9, rp10, rp11, rp12])
        rp13 = side.add_reference_point(self.blue_side_name + 'xl_point13', point_1[0][0], point_1[0][1])
        rp14 = side.add_reference_point(self.blue_side_name + 'xl_point14', point_1[1][0], point_1[1][1])
        rp15 = side.add_reference_point(self.blue_side_name + 'xl_point15', point_1[3][0], point_1[3][1])
        rp16 = side.add_reference_point(self.blue_side_name + 'xl_point16', point_1[2][0], point_1[2][1])
        point_list.append([rp13, rp14, rp15, rp16])
        rp17 = side.add_reference_point(self.blue_side_name + 'xl_point17', point_1[0][0], point_1[0][1])
        rp18 = side.add_reference_point(self.blue_side_name + 'xl_point18', point_1[1][0], point_1[1][1])
        rp19 = side.add_reference_point(self.blue_side_name + 'xl_point19', point_1[3][0], point_1[3][1])
        rp20 = side.add_reference_point(self.blue_side_name + 'xl_point20', point_1[2][0], point_1[2][1])
        point_list.append([rp17, rp18, rp19, rp20])

        return point_list

    # 创建警戒区
    def creat_prosecution_area(self,side):
        point_list = []
        # latitude = '22.3113595300641', longitude = '121.15216743137'
        # latitude = '22.3096610150021', longitude = '124.463645678287'
        # latitude = '20.8369967989404', longitude = '124.447607198609'
        # latitude = '20.8031602880006', longitude = '121.151376333954'
        point_1 = [(22.3113595300641, 121.15216743137), (22.3096610150021, 124.463645678287),
                   (20.8369967989404, 124.447607198609), (20.8031602880006, 121.151376333954)]
        jj1 = side.add_reference_point(self.blue_side_name + 'jj1', point_1[0][0], point_1[0][1])
        jj2 = side.add_reference_point(self.blue_side_name + 'jj2', point_1[1][0], point_1[1][1])
        jj3 = side.add_reference_point(self.blue_side_name + 'jj3', point_1[2][0], point_1[2][1])
        jj4 = side.add_reference_point(self.blue_side_name + 'jj4', point_1[3][0], point_1[3][1])
        point_list.append([jj1, jj2, jj3, jj4])
        jj5 = side.add_reference_point(self.blue_side_name + 'jj5', point_1[0][0], point_1[0][1])
        jj6 = side.add_reference_point(self.blue_side_name + 'jj6', point_1[1][0], point_1[1][1])
        jj7 = side.add_reference_point(self.blue_side_name + 'jj7', point_1[2][0], point_1[2][1])
        jj8 = side.add_reference_point(self.blue_side_name + 'jj8', point_1[3][0], point_1[3][1])
        point_list.append([jj5, jj6, jj7, jj8])
        jj9 = side.add_reference_point(self.blue_side_name + 'jj9', point_1[0][0], point_1[0][1])
        jj10 = side.add_reference_point(self.blue_side_name + 'jj10', point_1[1][0], point_1[1][1])
        jj11 = side.add_reference_point(self.blue_side_name + 'jj11', point_1[2][0], point_1[2][1])
        jj12 = side.add_reference_point(self.blue_side_name + 'jj12', point_1[3][0], point_1[3][1])
        point_list.append([jj9, jj10, jj11, jj12])
        jj13 = side.add_reference_point(self.blue_side_name + 'jj13', point_1[0][0], point_1[0][1])
        jj14 = side.add_reference_point(self.blue_side_name + 'jj14', point_1[1][0], point_1[1][1])
        jj15 = side.add_reference_point(self.blue_side_name + 'jj15', point_1[2][0], point_1[2][1])
        jj16 = side.add_reference_point(self.blue_side_name + 'jj16', point_1[3][0], point_1[3][1])
        point_list.append([jj13, jj14, jj15, jj16])
        jj17 = side.add_reference_point(self.blue_side_name + 'jj17', point_1[0][0], point_1[0][1])
        jj18 = side.add_reference_point(self.blue_side_name + 'jj18', point_1[1][0], point_1[1][1])
        jj19 = side.add_reference_point(self.blue_side_name + 'jj19', point_1[2][0], point_1[2][1])
        jj20 = side.add_reference_point(self.blue_side_name + 'jj20', point_1[3][0], point_1[3][1])
        point_list.append([jj17, jj18, jj19, jj20])

        return point_list
    # 设置巡逻任务条令
    def edit_weapon_doctrine(self, doctrine):
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
    def _construct_side_entity(self):
        """
        构造各方实体
        """
        self.redside = self.scenario.get_side_by_name(self.red_side_name)
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name(self.blue_side_name)
        self.blueside.static_construct()
    def _init_unit_list(self):
        """
        初始化单元列表
        """
        self.blue_unit_dict_list = self._init_blue_unit_dict()
        self.red_unit_dict = self._init_red_unit_dict()
    def _init_blue_unit_dict(self):
        """
        初始化蓝方单元列表
        """
        all_blue_aircraft_dict_list = []
        blue_aircraft_dict_1 = {aircraft_key: aircraft_value for aircraft_key,aircraft_value in self.blueside.aircrafts.items() if
                                  aircraft_value.strName in self.lst_1}
        all_blue_aircraft_dict_list.append(blue_aircraft_dict_1)
        blue_aircraft_dict_2 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in
                                self.blueside.aircrafts.items() if
                                aircraft_value.strName in self.lst_2}
        all_blue_aircraft_dict_list.append(blue_aircraft_dict_2)
        blue_aircraft_dict_3 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in
                                self.blueside.aircrafts.items() if
                                aircraft_value.strName in self.lst_3}
        all_blue_aircraft_dict_list.append(blue_aircraft_dict_3)
        blue_aircraft_dict_4 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in
                                self.blueside.aircrafts.items() if
                                aircraft_value.strName in self.lst_4}
        all_blue_aircraft_dict_list.append(blue_aircraft_dict_4)
        blue_aircraft_dict_5 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in
                                self.blueside.aircrafts.items() if
                                aircraft_value.strName in self.lst_5}
        all_blue_aircraft_dict_list.append(blue_aircraft_dict_5)
        return all_blue_aircraft_dict_list
    def _init_red_unit_dict(self):
        """
        初始化红方单元列表
        """
        red_aircraft_dict = {aircraft_key:aircraft_value for aircraft_key,aircraft_value in self.redside.aircrafts.items() if
                             '米格' in aircraft_value.strName}
        return red_aircraft_dict
    def get_observation(self):
        """
        获取红蓝双方飞机的经纬度、朝向，作为模型的state，即输入到模型，
        """
        blue_aircraft_unit_dict = self.blue_unit_dict_list
        blue_obs = self.get_blue_side_observation(blue_aircraft_unit_dict)

        self.observation = blue_obs
        return blue_obs
    def get_blue_side_observation(self,unit_dict_list):
        blue_obs_all = np.zeros((5,6))
        for i in range(len(unit_dict_list)):
            blue_obs_lt = []
            for key, unit in unit_dict_list[i].items():
                if key:
                    blue_obs_lt.append(unit.dLongitude)
                    blue_obs_lt.append(unit.dLatitude)
                    blue_obs_lt.append(unit.fCurrentHeading)
            blue_obs_all[i,:] = blue_obs_lt
        return blue_obs_all
    def reset(self):
        # 调用父类的重置函数
        super(feihaiblue_mappo_aircraft, self).reset()

        # 构建各方实体
        self._construct_side_entity()
        self._init_unit_list()
        # 构建9宫格
        self.init_train_zone()
        # 先初始化一个巡逻任务，让飞机动起来
        self.init_creat_patrol_mission()
        # self.update_patrol_mission()
        state_now = self.get_observation()
        # reward_now = self.get_reward(None)
        return state_now
    '''
    execute_action函数就是通常所说的step函数
    流程： 
        输入动作：就是9个离散区域之一
        执行动作：更新巡逻区
        更新态势
        获取观察
        获取reward
        检查是否结束
        如果最后收敛的情况下，会选择一个最好的区域，并且保持不变        
    参数：无
    返回： 1）state：状态；
           2）reward：回报值
    '''
    def execute_action(self, action):
        super(feihaiblue_mappo_aircraft, self).step()
        nine_zone = self.train_zones
        print('action=', action)
        # final_patrol_zone = nine_zone[action[i]]
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        self.update_patrol_mission_zone(self.blueside, nine_zone, action)
        self.update_presection_zone(self.blueside, nine_zone, action)
        # 动作下达了，该仿真程序运行，以便执行指令
        self.mozi_server.run_grpc_simulate()

        # 更新数据时，会被阻塞，实现与仿真的同步
        self._update()

        obs = self.get_observation()
        reward = self.get_reward(nine_zone, action)
        done = self.check_done()

        return obs, reward, done

    def update_patrol_mission_zone(self, side, nine_zone, action):
        # 利用学习到动作值，更新巡逻区
        # 利用学习到动作值，找到相应区域，然后利用区域中心，生成小范围巡逻区
        for i, zone_index in zip([1,5,9,13,17], action):
            final_zone = nine_zone[zone_index]
            central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
            central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
            side.set_reference_point(self.blue_side_name + 'xl_point' + str(i+0), central_lat + 0.03, central_lon - 0.05)
            side.set_reference_point(self.blue_side_name + 'xl_point' + str(i+1), central_lat + 0.04, central_lon + 0.06)
            side.set_reference_point(self.blue_side_name + 'xl_point' + str(i+2), central_lat - 0.04, central_lon + 0.05)
            side.set_reference_point(self.blue_side_name + 'xl_point' + str(i+3), central_lat - 0.03, central_lon - 0.06)
    def update_presection_zone(self,side, nine_zone, action):
        # 利用学习到动作值，更新警戒区
        for i, zone_index in zip([1,5,9,13,17], action):
            final_zone = nine_zone[zone_index]
            side.set_reference_point(self.blue_side_name + 'jj' + str(i+0), final_zone[0][0], final_zone[0][1])
            side.set_reference_point(self.blue_side_name + 'jj' + str(i+1), final_zone[1][0], final_zone[1][1])
            side.set_reference_point(self.blue_side_name + 'jj' + str(i+2), final_zone[3][0], final_zone[3][1])
            side.set_reference_point(self.blue_side_name + 'jj' + str(i+3), final_zone[2][0], final_zone[2][1])
    def _update(self):
        """
        更新
        """
        # self.mozi_server.update_situation(self.scenario, self.app_mode)
        self.redside.static_update()
        self.blueside.static_update()
    def get_reward(self, nine_zone, action):
        """
        获取奖励，最终奖励设置原则是选择包含红方飞机最多的，且离蓝方飞机最近的格子
        """
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        reward_all_agent = []
        for zone_index in action:
            action_for_final_patrol_zone = nine_zone[zone_index]
            if action_for_final_patrol_zone is not None:
                # 在某个格子内，包括红方飞机数量越多，奖励值越大

                num_reward = self._get_num_reward(action_for_final_patrol_zone) / 10
                # 获取得分奖励，战损战果
                score_reward = float(self.blueside.iTotalScore) / 300
                # 获得距离得分，蓝方一架飞机距离格子中心点小于60公里，则加1分，否则减1分
                distance_reward = self._get_distance_reward(action_for_final_patrol_zone)
                # 对三个reward 进行加权求和作为总reward
                reward_all_agent.append(0.3 * num_reward + 0.1 * score_reward + 0.6 * distance_reward)
        return reward_all_agent

    def _get_num_reward(self, final_zone):
        # 获得该区域内红方飞机数量，数量越多，reward越大
        zone_ref = [{'latitude': v[0], 'longitude': v[1]} for v in final_zone]
        num = 0
        for k,v in self.red_unit_dict.items():
            unit = {}
            unit['latitude'] = v.dLatitude
            unit['longitude'] = v.dLongitude
            if zone_contain_unit(zone_ref, unit):
                num += 1
        return num

    def _get_distance_reward(self, final_zone):
        # 由于蓝方飞机是集体行动的，判断和格子中心点的距离，10架里最远的距离小于80，加1分，否则减1分
        # 设置这个reward的目的是选择离蓝方飞机最近的格子，
        dis_reward = 0
        all_agent_dis = []
        # 获取格子中心点坐标
        central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
        central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
        for blue_unit_dict in self.blue_unit_dict_list:
            for blue_unit_dict_value in blue_unit_dict.values():
                dis = get_horizontal_distance((blue_unit_dict_value.dLatitude, blue_unit_dict_value.dLongitude),(central_lat, central_lon))
                all_agent_dis.append(dis)
        if np.max(all_agent_dis) < 80:
            dis_reward += 1
        else:
            dis_reward -= 1
        return dis_reward

    def check_done(self):
        # 判断是否结束，如果蓝方飞机都打没了，结束，红方飞机都打没了，结束，否则继续
        done_list = []
        for i in range(len(self.blue_unit_dict_list)):
            if len(self.blue_unit_dict_list[i]) == 0 and len(self.red_unit_dict) == 0:
                done_list.append(True)
            else:
                done_list.append(False)
        return done_list
