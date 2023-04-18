#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import random
from blue_agent_lj.feihai_blue_ppo_v4_train_aircraft_lk_and_zzh.envs.utils import *
from mozi_ai_sdk.base_env import BaseEnvironment


'''
作者：
日期：
功能：
'''
class feihaiblue(BaseEnvironment):
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
        self.observation_space = 60  # 状态空间维度
        self.action_space = 9
        self.action_max = 8
        self.blue_unit_dict = None
        self.red_unit_dict = None
        self.observation = None
        self.red_side_name = "红方"
        self.blue_side_name = "蓝方"
        self.lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
        self.lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']
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

    # 先创建一个巡逻任务，让飞机动起来，然后利用学习出来的区域更新巡逻区
    def init_creat_patrol_mission(self):
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        flag = self.scenario.mozi_server.get_value_by_key(f'{self.blue_side_name}巡逻任务已创建')
        if flag == 'Yes':
            return False
        nine_zone = self.train_zones
        # 从9个区域里随机找一个，作为初始巡逻区
        patrol_zone_start = random.choice(nine_zone)
        point_list = self.create_patrol_zone(self.blueside, patrol_zone_start)
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
            patrolmssn.set_one_third_rule('false')
            patrolmssn.set_patrol_zone(point_str)
            patrolmssn.set_prosecution_zone(ps_str)
            airs_xl1 = self.blue_unit_dict
            patrolmssn.assign_units(airs_xl1)
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
        self.scenario.mozi_server.set_key_value(f'{self.blue_side_name}巡逻任务已创建', 'Yes')
    # 用随机选择的一个区域作为初始巡逻的巡逻区
    def create_patrol_zone(self, side, point_1):
        point_list = []
        rp1 = side.add_reference_point(self.blue_side_name + 'xl_point1', point_1[0][0], point_1[0][1])
        rp2 = side.add_reference_point(self.blue_side_name + 'xl_point2', point_1[1][0], point_1[1][1])
        rp3 = side.add_reference_point(self.blue_side_name + 'xl_point3', point_1[3][0], point_1[3][1])
        rp4 = side.add_reference_point(self.blue_side_name + 'xl_point4', point_1[2][0], point_1[2][1])
        point_list.append([rp1, rp2, rp3, rp4])
        return point_list
    # 给初始巡逻任务添加飞机，设置条例
    '''
        def update_patrol_mission(self):
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        patrol_missions_dic = self.blueside.get_patrol_missions()
        patrol_missions = [mission for mission in patrol_missions_dic.values()]
        print('patrol_missions=',patrol_missions)
        if len(patrol_missions) == 0:
            return False
        point_prosecution_list = self.creat_prosecution_area(self.blueside)
        ps_str = []
        for ps in point_prosecution_list:
            for name in ps:
                ps_str.append(name.strName)
        # 如果有任务，就每个任务更新，包含给任务分配飞机，1/3规则
        for patrol_mission in patrol_missions:
            if patrol_mission.strName == self.blue_side_name + 'xl1':
                patrol_mission.set_prosecution_zone(ps_str)
                doctrine_xl1 = patrol_mission.get_doctrine()
                doctrine_xl1.set_weapon_state_for_aircraft(2002)
                doctrine_xl1.set_weapon_state_for_air_group('3')
                doctrine_xl1.gun_strafe_for_aircraft('1')
                # AGM-84L:816,AIM-120C-7:718,AIM-9M:1384
                self.edit_weapon_doctrine(doctrine=doctrine_xl1)
                # 5,6,7号飞机
                airs_xl1 = self.blue_unit_dict
                print('airs_xl1=',airs_xl1)
                patrol_mission.assign_units(airs_xl1)
                patrol_mission.set_flight_size(1)
                patrol_mission.set_flight_size_check('false')
                patrol_mission.set_opa_check('true')
                patrol_mission.set_wwr_check('true')
                patrol_mission.set_emcon_usage('false')
    '''

    # 创建警戒区
    def creat_prosecution_area(self,side):
        point_list = []
        # latitude = '22.3113595300641', longitude = '121.15216743137'
        # latitude = '22.3096610150021', longitude = '124.463645678287'
        # latitude = '20.8369967989404', longitude = '124.447607198609'
        # latitude = '20.8031602880006', longitude = '121.151376333954'
        point_1 = [(22.3113595300641, 121.15216743137), (22.3096610150021, 124.463645678287),
                   (20.8369967989404, 124.447607198609), (20.8031602880006, 121.151376333954)]
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
        self.blue_unit_dict = self._init_blue_unit_dict()
        self.red_unit_dict = self._init_red_unit_dict()
    def _init_blue_unit_dict(self):
        """
        初始化蓝方单元列表
        """
        blue_aircraft_dict = {aircraft_key: aircraft_value for aircraft_key,aircraft_value in self.blueside.aircrafts.items() if
                                  aircraft_value.strName in self.lst_1 + self.lst_2}
        return blue_aircraft_dict
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
        blue_aircraft_unit_dict = self.blue_unit_dict
        blue_obs = self.get_blue_side_observation(blue_aircraft_unit_dict)
        red_aircraft_unit_dict = self.red_unit_dict
        red_obs = self.get_red_side_observation(red_aircraft_unit_dict)
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
    '''
    def reset(self):
        # 调用父类的重置函数
        super(feihaiblue, self).reset()

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
    def reset_ppo(self):
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
        # super(feihaiblue, self).step()
        nine_zone = self.train_zones
        print('action=', action)
        final_patrol_zone = nine_zone[action]
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        self.update_patrol_mission_zone(self.blueside, final_patrol_zone)
        self.update_presection_zone(self.blueside, final_patrol_zone)
        # 动作下达了，该仿真程序运行，以便执行指令
        self.mozi_server.run_grpc_simulate()

        # 更新数据时，会被阻塞，实现与仿真的同步
        self._update()

        obs = self.get_observation()
        reward = self.get_reward(final_patrol_zone)
        done = self.check_done()

        return np.array(obs), reward, done

    def update_patrol_mission_zone(self, side, final_zone):
        # 利用学习到动作值，更新巡逻区
        # 利用学习到动作值，找到相应区域，然后利用区域中心，生成小范围巡逻区
        central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
        central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
        side.set_reference_point(self.blue_side_name + 'xl_point1', central_lat + 0.03, central_lon - 0.05)
        side.set_reference_point(self.blue_side_name + 'xl_point2', central_lat + 0.04, central_lon + 0.06)
        side.set_reference_point(self.blue_side_name + 'xl_point3', central_lat - 0.04, central_lon + 0.05)
        side.set_reference_point(self.blue_side_name + 'xl_point4', central_lat - 0.03, central_lon - 0.06)
    def update_presection_zone(self,side, final_zone):
        # 利用学习到动作值，更新警戒区
        side.set_reference_point(self.blue_side_name + 'jj5', final_zone[0][0], final_zone[0][1])
        side.set_reference_point(self.blue_side_name + 'jj6', final_zone[1][0], final_zone[1][1])
        side.set_reference_point(self.blue_side_name + 'jj7', final_zone[3][0], final_zone[3][1])
        side.set_reference_point(self.blue_side_name + 'jj8', final_zone[2][0], final_zone[2][1])
    def _update(self):
        """
        更新
        """
        # self.mozi_server.update_situation(self.scenario, self.app_mode)
        self.redside.static_update()
        # self.blueside.static_update()
    def get_reward(self, action_for_final_patrol_zone):
        """
        获取奖励，最终奖励设置原则是选择包含红方飞机最多的，且离蓝方飞机最近的格子
        """
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        reward = 0.0
        if action_for_final_patrol_zone is not None:
            # 在某个格子内，包括红方飞机数量越多，奖励值越大

            num_reward = self._get_num_reward(action_for_final_patrol_zone) / 10
            print('num_reward=', num_reward)
            # 获取得分奖励，战损战果
            score_reward = float(self.blueside.iTotalScore) / 300
            print('score_reward=', score_reward)
            # 获得距离得分，蓝方一架飞机距离格子中心点小于60公里，则加1分，否则减1分
            distance_reward = self._get_distance_reward(action_for_final_patrol_zone)
            print('distance_reward=', distance_reward)
            # 对三个reward 进行加权求和作为总reward
            reward = 0.3 * num_reward + 0.1 * score_reward + 0.6 * distance_reward
        return reward
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
    '''

    def _get_num_reward(self, final_zone):
        # 获得该区域内红方飞机数量，数量越多，reward越大
        central_lat = (final_zone[0][0] + final_zone[2][0]) / 2
        central_lon = (final_zone[0][1] + final_zone[1][1]) / 2
        dis_list = []
        num_reward = 0
        for air in self.red_unit_dict.values():
            dis = get_horizontal_distance((air.dLatitude, air.dLongitude), (central_lat, central_lon))
            dis_list.append(dis)
        dis_nearest = [True for d in dis_list if d < 60]
        if len(dis_nearest) != 0:
            num_reward = len(dis_nearest)
        return num_reward

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

    def check_done(self):
        # 判断是否结束，如果蓝方飞机都打没了，结束，红方飞机都打没了，结束，否则继续
        if len(self.blue_unit_dict) == 0 or len(self.red_unit_dict) == 0:
            return True
        else:
            return False
