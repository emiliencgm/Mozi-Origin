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
功能：打船的环境文件
'''
class feihaiblue_ship(BaseEnvironment):
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
        self.observation_space = 33  # 状态空间维度
        self.action_space = 2 # 连续型动作[x,x]
        # self.action_max = 8
        self.blue_unit_dict = None
        self.red_unit_dict = None
        self.observation = None
        self.red_side_name = "红方"
        self.blue_side_name = "蓝方"
        self.lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
        self.lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']
        self.lst_3 = ['F-16A #01', 'F-16A #02', 'F-16A #03', 'F-16A #04']
        self.lst_4 = ['F-16A #1', 'F-16A #2', 'F-16A #3', 'F-16A #4']
        self.lst_5 = ['E-2K #1']
        self.lst_6 = ['EC-130H #1']
        self.lst_7 = ['EC-130H #2']
        self.train_zones = None
    def init_train_zone(self):
        # 初始化9宫格
        # 对于打船，不需要这个函数
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

    # 先创建一个支援任务，让干扰机、预警机动起来，采用固定区域，夺得制空权，为后续打船训练做准备
    def init_creat_support_mission(self):
        flag = self.scenario.mozi_server.get_value_by_key(f'{self.blue_side_name}支援任务已创建')
        if flag == 'Yes':
            return False
        support_point_list = self.support_zone_for_three(self.blueside)
        airs_support1 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in
                              self.blueside.aircrafts.items() if
                              aircraft_value.strName in self.lst_5 + self.lst_6 + self.lst_7}
        for air in airs_support1.values():
            if air.strName == 'E-2K #1':
                doctrine = air.get_doctrine()
                doctrine.set_em_control_status('Radar', 'Active')
            elif air.strName in ['EC-130H #1', 'EC-130H #2']:
                doctrine = air.get_doctrine()
                doctrine.set_em_control_status('OECM', 'Active')
        for point in support_point_list:
            point_str_support = []
            for name in point:
                point_str_support.append(name.strName)
            support_name = self.blue_side_name + 'support' + str(1)
            supportmssn = self.blueside.add_mission_support(support_name, point_str_support)
            print('支援任务1已创建')
            supportmssn.set_is_active('true')
            supportmssn.assign_units(airs_support1)
            supportmssn.set_one_third_rule('false')
            supportmssn.set_flight_size(1)
            supportmssn.set_flight_size_check('false')
        self.scenario.mozi_server.set_key_value(f'{self.blue_side_name}支援任务已创建', 'Yes')
    # 先创建一个巡逻任务，让飞机动起来，采用固定区域，夺得制空权，为后续打船训练做准备
    def init_creat_patrol_mission(self):
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        flag = self.scenario.mozi_server.get_value_by_key(f'{self.blue_side_name}巡逻任务已创建')
        if flag == 'Yes':
            return False
        # nine_zone = self.train_zones
        # # 从9个区域里随机找一个，作为初始巡逻区
        # patrol_zone_start = random.choice(nine_zone)
        point_list = self.create_patrol_zone(self.blueside)
        i = 1
        point_prosecution_list = self.creat_prosecution_area(self.blueside)
        ps_str = []
        for ps in point_prosecution_list:
            for name in ps:
                ps_str.append(name.strName)
        for point in point_list:
            point_str = []
            for name in point:
                point_str.append(name.strName)
            # 新建巡逻区名字
            patrol_name = self.blue_side_name + 'xl' + str(i)
            patrolmssn = self.blueside.add_mission_patrol(patrol_name, 0, point_str)
            print('巡逻任务已创建')
            patrolmssn.set_one_third_rule('false')
            patrolmssn.set_patrol_zone(point_str)
            patrolmssn.set_prosecution_zone(ps_str)
            airs_xl1 = {aircraft_key: aircraft_value for aircraft_key, aircraft_value in self.blueside.aircrafts.items()
                        if aircraft_value.strName in self.lst_1 + self.lst_2}
            patrolmssn.assign_units(airs_xl1)
            patrolmssn.set_flight_size(1)
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
        self.scenario.mozi_server.set_key_value(f'{self.blue_side_name}巡逻任务已创建', 'Yes')
    # 用固定区域作为初始支援任务的支援区
    def support_zone_for_three(self, side):
        point_list = []
        point_1 = [(22.4098475117646, 122.186072181501), (22.418764139488, 122.367143273071),
                   (22.233752742808, 122.386191481229), (22.2336414046035, 122.186317353378)]
        rp20 = side.add_reference_point(self.blue_side_name + 'xl_support1', point_1[0][0], point_1[0][1])
        rp21 = side.add_reference_point(self.blue_side_name + 'xl_support2', point_1[1][0], point_1[1][1])
        rp22 = side.add_reference_point(self.blue_side_name + 'xl_support3', point_1[2][0], point_1[2][1])
        rp23 = side.add_reference_point(self.blue_side_name + 'xl_support4', point_1[3][0], point_1[3][1])
        point_list.append([rp20, rp21, rp22, rp23])
        return point_list
    # 用固定区域作为初始巡逻的巡逻区
    def create_patrol_zone(self, side):
        point_list = []
        point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
                   (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
        rp1 = side.add_reference_point(self.blue_side_name + 'xl_point1', point_1[0][0], point_1[0][1])
        rp2 = side.add_reference_point(self.blue_side_name + 'xl_point2', point_1[1][0], point_1[1][1])
        rp3 = side.add_reference_point(self.blue_side_name + 'xl_point3', point_1[2][0], point_1[2][1])
        rp4 = side.add_reference_point(self.blue_side_name + 'xl_point4', point_1[3][0], point_1[3][1])
        point_list.append([rp1, rp2, rp3, rp4])
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
        point_1 = [(21.813803192903, 122.369519984786), (21.8326948541021, 122.521524522641),
                   (21.6821653996223, 122.531658874429), (21.6914739156693, 122.349410016875)]
        rp5 = side.add_reference_point(self.blue_side_name + 'jj5', point_1[0][0], point_1[0][1])
        rp6 = side.add_reference_point(self.blue_side_name + 'jj6', point_1[1][0], point_1[1][1])
        rp7 = side.add_reference_point(self.blue_side_name + 'jj7', point_1[2][0], point_1[2][1])
        rp8 = side.add_reference_point(self.blue_side_name + 'jj8', point_1[3][0], point_1[3][1])
        point_list.append([rp5, rp6, rp7, rp8])
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

    def edit_anti_ship_weapon_doctrine(self, doctrine):
        # AGM - 84L: 816
        doctrine.set_weapon_release_authority('816', '2999', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3101', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3102', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3103', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3000', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3104', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3105', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3106', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3107', '2', '1', '80', 'none', 'false')
        doctrine.set_weapon_release_authority('816', '3108', '2', '1', '80', 'none', 'false')
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
        初始化单元列表,blue_unit_dict是初始化打船的飞机,red_unit_dict是三艘船
        """
        self.blue_unit_dict = self._init_blue_unit_dict()
        self.red_unit_dict = self._init_red_unit_dict()
    def _init_blue_unit_dict(self):
        """
        初始化蓝方单元列表,这次是初始化打船的飞机
        """
        blue_aircraft_dict = {aircraft_key: aircraft_value for aircraft_key,aircraft_value in self.blueside.aircrafts.items() if
                                  aircraft_value.strName in self.lst_3 + self.lst_4}
        return blue_aircraft_dict
    def _init_red_unit_dict(self):
        """
        初始化红方单元列表
        """
        red_ship_dict = {ship_key:ship_value for ship_key,ship_value in self.redside.ships.items() if
                             '护卫舰' in ship_value.strName or '驱逐舰' in ship_value.strName or '航空母舰' in ship_value.strName}
        return red_ship_dict
    def get_observation(self):
        """
        获取红蓝双方的经纬度、朝向，作为模型的state，即输入到模型，
        """
        blue_aircraft_unit_dict = self.blue_unit_dict
        blue_obs = self.get_blue_side_observation(blue_aircraft_unit_dict)
        red_ship_unit_dict = self.red_unit_dict
        red_obs = self.get_red_side_observation(red_ship_unit_dict)
        all_obs_array = np.array(blue_obs + red_obs)
        self.observation = all_obs_array
        return all_obs_array
    def get_blue_side_observation(self,unit_dict):
        blue_obs_lt = []
        for key, unit in unit_dict.items():
            if key:
                blue_obs_lt.append(unit.dLongitude)
                blue_obs_lt.append(unit.dLatitude)
                blue_obs_lt.append(unit.fCurrentHeading)
        return blue_obs_lt
    def get_red_side_observation(self,unit_dict):
        red_obs_lt = []
        for key, unit in unit_dict.items():
            if key:
                red_obs_lt.append(unit.dLongitude)
                red_obs_lt.append(unit.dLatitude)
                red_obs_lt.append(unit.fCurrentHeading)
        return red_obs_lt

    def reset(self):
        # 调用父类的重置函数
        super(feihaiblue_ship, self).reset()

        # 构建各方实体
        self._construct_side_entity()
        self._init_unit_list()
        # 构建9宫格
        # self.init_train_zone()
        # 先初始化一个巡逻任务，让飞机动起来
        self.init_creat_patrol_mission()
        # 先初始化一个支援任务，让干扰机动起来
        self.init_creat_support_mission()
        state_now = self.get_observation()
        # reward_now = self.get_reward(None)
        return state_now
    '''
    execute_action函数就是通常所说的step函数
    流程： 
        输入动作：就是经纬度的偏差，[-1,1]之间的两个值
        执行动作：给打船飞机设置航路点，让他远离敌方船，在安全距离开会
        更新态势
        获取观察
        获取reward
        检查是否结束
        如果最后收敛的情况下，会选择一个最好的偏差值，这个偏差值加在护卫舰的坐标上，成为打船飞机的航路点     
    参数：无
    返回： 1）state：状态；
           2）reward：回报值
    '''
    def execute_action(self, action):
        super(feihaiblue_ship, self).step()
        # 首先下达一个对海打击任务，让飞机飞出去，然后利用学习出来的偏差值，设置航路点
        print('action=',action)

        flag = self.create_strike_ship_mission(self.blueside)
        if not flag:
            # 如果已经有打击任务了，就不在创建了，直接利用学习到action设置航路点

            self.set_plot_point(action)
        # 动作下达了，该仿真程序运行，以便执行指令
        self.mozi_server.run_grpc_simulate()

        # 更新数据时，会被阻塞，实现与仿真的同步
        self._update()

        obs = self.get_observation()
        reward = self.get_reward(action)
        done = self.check_done()

        return np.array(obs), reward, done

    def update_support_zone(self,side):
        # 预警机、干扰机前推
        point_2 = [(19.8452434017736, 124.15306856036), (19.8608816443815, 124.258533532556),
                   (19.7773499598268, 124.258482921611), (19.756491023618, 124.16971312762)]
        side.set_reference_point(self.blue_side_name + 'xl_support1', point_2[0][0], point_2[0][1])
        side.set_reference_point(self.blue_side_name + 'xl_support2', point_2[1][0], point_2[1][1])
        side.set_reference_point(self.blue_side_name + 'xl_support3', point_2[2][0], point_2[2][1])
        side.set_reference_point(self.blue_side_name + 'xl_support4', point_2[3][0], point_2[3][1])

    def create_strike_ship_mission(self,side):

        mssnSitu = side.strikemssns
        if {k: v for k, v in mssnSitu.items() if v.strName == 'strike1'}.__len__() == 0:
            strkmssn_1 = side.add_mission_strike('strike1', 2)
            # 取消满足编队规模才能起飞的限制（任务条令）
            strkmssn_1.set_start_time('2021-05-26 12:00:00')
            strkmssn_1.set_flight_size(1)
            strkmssn_1.set_flight_size_check('false')
            strike_target = {key:value for key,value in self.red_unit_dict.items() if '护卫舰' in value.strName}
            for k, v in self.red_unit_dict.items():
            # set_mark_contact设置目标对抗关系,H is 敌方
                side.set_mark_contact(k, 'H')
            for k, v in self.red_unit_dict.items():
                strkmssn_1.assign_unit_as_target(k)
            strkmssn_1.assign_units(self.blue_unit_dict)
            strkmssn_1.add_plan_way_to_mission(0, '航线2')
            return True
        else:
            return False
    def set_plot_point(self,action):
        target_huwei = [value for key, value in self.red_unit_dict.items() if '护卫舰' in value.strName]
        if len(target_huwei) != 0 :
            geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
            doctrine = self.blueside.get_doctrine()
            for air in self.blue_unit_dict.values():
                if '返回基地' in air.strActiveUnitStatus:
                    continue
                # doctrine = air.get_doctrine()
                # doctrine.set_emcon_according_to_superiors('no')
                # doctrine.set_em_control_status('Radar', 'Passive')
                self.evade_ship(geopoint_target, air, doctrine, action)
    def evade_ship(self,geopoint_target, air, mission_doctrine, action):
        geopoint_air = (air.dLatitude, air.dLongitude)
        dis = get_horizontal_distance(geopoint_air, geopoint_target)
        if dis <= 150:
            self.update_support_zone(self.blueside)
            mission_doctrine.ignore_plotted_course('yes')
            genpoint_away = (geopoint_target[0] + action[0], geopoint_target[1] + action[1])
            air.plot_course([genpoint_away])
            self.edit_anti_ship_weapon_doctrine(mission_doctrine)

    '''
        def update_patrol_mission_zone(self, side, final_zone):
        # 利用学习到动作值，更新巡逻区,对于打船，没有用
        # 利用学习到动作值，找到相应区域，然后利用区域中心，生成小范围巡逻区
        central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
        central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
        side.set_reference_point(self.blue_side_name + 'xl_point1', central_lat + 0.03, central_lon - 0.05)
        side.set_reference_point(self.blue_side_name + 'xl_point2', central_lat + 0.04, central_lon + 0.06)
        side.set_reference_point(self.blue_side_name + 'xl_point3', central_lat - 0.04, central_lon + 0.05)
        side.set_reference_point(self.blue_side_name + 'xl_point4', central_lat - 0.03, central_lon - 0.06)
    '''

    def _update(self):
        """
        更新
        """
        # self.mozi_server.update_situation(self.scenario, self.app_mode)
        self.redside.static_update()
        self.blueside.static_update()
    def get_reward(self, action):
        """
        获取奖励，最终奖励设置原则是离护卫舰距离在50-60之间，加分，离驱逐舰距离在70-80之间加分
        """
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        reward = 0.0
        if len(action) != 0:
            if abs(action[0]) < 0.2 and abs(action[1]) < 0.3:
                distance_reward_1 = self._get_dis_for_huwei_reward() / 8
                # 获取得分奖励，战损战果
                score_reward = self.check_target_alive()
                # 获得距离得分
                distance_reward_2 = self._get_dis_for_quzhu_reward() / 8
                # 对三个reward 进行加权求和作为总reward
                reward = 0.4 * distance_reward_1 + 0.2 * score_reward + 0.4 * distance_reward_2
            else:
                reward -= 0.5
        return reward

    def _get_dis_for_huwei_reward(self):
        dis_reward = 0
        target_huwei = [value for key, value in self.red_unit_dict.items() if '护卫舰' in value.strName]
        if len(target_huwei) != 0:
            geopoint_target = (target_huwei[0].dLatitude, target_huwei[0].dLongitude)
            for air in self.blue_unit_dict.values():
                geopoint_air = (air.dLatitude, air.dLongitude)
                dis = get_horizontal_distance(geopoint_air, geopoint_target)
                if 50 < dis < 60:
                    dis_reward += 1
                else:
                    dis_reward -= 1
        return dis_reward

    def _get_dis_for_quzhu_reward(self):
        dis_reward = 0
        target_quzhu = [value for key, value in self.red_unit_dict.items() if '驱逐舰' in value.strName]
        if len(target_quzhu) != 0:
            geopoint_target = (target_quzhu[0].dLatitude, target_quzhu[0].dLongitude)
            for air in self.blue_unit_dict.values():
                geopoint_air = (air.dLatitude, air.dLongitude)
                dis = get_horizontal_distance(geopoint_air, geopoint_target)
                if 70 < dis < 80:
                    dis_reward += 1
                else:
                    dis_reward -= 1
        return dis_reward

    def check_target_alive(self):
        reward_alive = 0
        target_quzhu = [value for key, value in self.red_unit_dict.items() if '驱逐舰' in value.strName]
        target_huwei = [value for key, value in self.red_unit_dict.items() if '护卫舰' in value.strName]
        if len(target_quzhu) == 0 or len(target_huwei) == 0:
            reward_alive += 1
        else:
            reward_alive -= 1
        return reward_alive

    '''
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
        # 由于蓝方飞机是集体行动的，所以从10架里随机选一架，判断和格子中心点的距离，小于60，加1分，否则减1分
        # 设置这个reward的目的是选择离蓝方飞机最近的格子，
        dis_reward = 0
        random_aircraft = random.choice(list(self.blue_unit_dict.values()))
        # 获取格子中心点坐标
        central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
        central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
        dis = get_horizontal_distance((random_aircraft.dLatitude, random_aircraft.dLongitude),(central_lat, central_lon))
        if dis < 60:
            dis_reward += 1
        else:
            dis_reward -= 1
        return dis_reward
    '''


    def check_done(self):
        # 判断是否结束，如果蓝方飞机都打没了，结束，红方飞机都打没了，结束，否则继续
        # if len(self.blue_unit_dict) == 0 or len(self.red_unit_dict) == 0:
        #     return True
        # else:
        #     return False
        # 对于打船，由于在最后执行，所以利用平台响应判断是否结束
        response_dic = self.scenario.get_responses()
        for _, v in response_dic.items():
            if v.Type == 'EndOfDeduction':
                print('打印出标记：EndOfDeduction')
                return True
        return False