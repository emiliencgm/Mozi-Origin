#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
本项目中的智能体执行
"""





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
from mozi_simu_sdk.group import CGroup
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
        self.action_space = 10 # 动作空间共 10 维，可派出 1 ~ 10 架执行巡逻任务
        self.action_max = 9 # 动作的返回值是 0 ~ 9，执行任务的飞机数量为 action + 1
        self.red_unit_dict_total = None
        self.blue_unit_dict = None # 执行巡逻任务的飞机编队
        self.blue_unit_dict_total = None # 全部飞机
        self.blue_unit_dict_avail = None # 目前可用的飞机
        self.observation = None
        self.red_side_name = "红方"
        self.blue_side_name = "蓝方"
        self.lst_1 = ['F-16A #7', 'F-16A #8', 'F-16A #9', 'F-16A #07', 'F-16A #08', 'F-16A #09']
        self.lst_2 = ['F-16A #5', 'F-16A #6', 'F-16A #05', 'F-16A #06']
        self.train_zones = None
        self.point_list = []

    


    # 先创建一个巡逻任务，让飞机动起来，然后利用学习出来的飞机编队设置更新巡逻任务
    def init_creat_patrol_mission(self):
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        flag = self.scenario.mozi_server.get_value_by_key(f'{self.blue_side_name}巡逻任务已创建')
        if flag == 'Yes':
            return False
        # 创建巡逻区 
        self.point_list = self.create_patrol_zone(self.blueside)
        
        # 创建警戒区
        point_prosecution_list = self.creat_prosecution_area(self.blueside)
        ps_str = []
        for ps in point_prosecution_list:
            for name in ps:
                ps_str.append(name.strName)
    
        i = 1
        for point in self.point_list:
            point_str = []
            for name in point:
                point_str.append(name.strName)
            # 新建巡逻区名字
            patrol_name = self.blue_side_name + 'xl' + str(i)

            # 创建巡逻任务，设置1/3规则
            patrolmssn = self.blueside.add_mission_patrol(patrol_name, 0, point_str)
            print('巡逻任务已创建')
            patrolmssn.set_one_third_rule('false')
            patrolmssn.set_patrol_zone(point_str)
            patrolmssn.set_one_third_rule('false')
            patrolmssn.set_patrol_zone(point_str)
            patrolmssn.set_prosecution_zone(ps_str)
            
            # 设置初始的巡逻任务编队，随机选择1架飞机
            airs_xl1 = self.blue_unit_dict
            print('当前的编队成员', [v.strName for k, v in airs_xl1.items()])
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
    
    def create_patrol_zone(self,side):
        """ 设置巡逻任务的巡逻区 """
        point_list = []
        point_1 = [(21.8210656716398, 122.356667127581), (21.8752434450009, 122.768058783733),
                (21.6701551543473, 122.35337044599), (21.6698815188537, 122.741326377829)]

        rp1 = side.add_reference_point(self.blue_side_name  + 'rp1', point_1[0][0], point_1[0][1])
        rp2 = side.add_reference_point(self.blue_side_name  + 'rp2', point_1[1][0], point_1[1][1])
        rp3 = side.add_reference_point(self.blue_side_name  + 'rp3', point_1[2][0], point_1[2][1])
        rp4 = side.add_reference_point(self.blue_side_name  + 'rp4', point_1[3][0], point_1[3][1])
        point_list.append([rp1, rp2, rp3, rp4])

        return point_list

    
    def creat_prosecution_area(self,side):
        """ 设置巡逻任务的警戒区 """
        point_list = []
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
        self.blue_unit_dict_total = self._init_blue_unit_dict_total()
        self.red_unit_dict_total = self._init_red_unit_dict_total()
        self.blue_unit_dict = self._init_blue_unit_dict()
        self.blue_unit_dict_avail = self.blue_unit_dict_total.items() - self.blue_unit_dict.items()
    
    def _init_blue_unit_dict(self):
        """
        初始蓝方作战飞机单元列表
        """
        random_aircraft = random.choice(list(self.blue_unit_dict_total.values()))
        blue_aircraft_dict = {aircraft_key: aircraft_value for aircraft_key,aircraft_value in self.blueside.aircrafts.items() if
                                  aircraft_value == random_aircraft}
        return blue_aircraft_dict
    def _init_blue_unit_dict_total(self):
        """ 
        初始化蓝方所有飞机单元列表
        """
        blue_aircraft_dict = {aircraft_key: aircraft_value for aircraft_key,aircraft_value in self.blueside.aircrafts.items() if
                                  aircraft_value.strName in self.lst_1 + self.lst_2}
        return blue_aircraft_dict
    def _init_red_unit_dict_total(self):
        """
        初始化红方单元列表
        """
        red_aircraft_dict = {aircraft_key:aircraft_value for aircraft_key,aircraft_value in self.redside.aircrafts.items() if
                             '米格' in aircraft_value.strName}
        return red_aircraft_dict
    def get_observation(self):
        """
        获取红蓝双方飞机的经纬度、朝向，作为模型的state，输入到模型
        """
        blue_aircraft_unit_dict = self.blue_unit_dict_total
        blue_obs = self.get_blue_side_observation(blue_aircraft_unit_dict)
        red_aircraft_unit_dict = self.red_unit_dict_total
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

    def reset(self):
        # 调用父类的重置函数
        super(feihaiblue, self).reset()

        # 构建各方实体
        self._construct_side_entity()
        self._init_unit_list() # 3个飞机字典

        # 先初始化一个巡逻任务，让飞机动起来
        self.init_creat_patrol_mission()
        # self.update_patrol_mission()
        state_now = self.get_observation()
        # reward_now = self.get_reward(None)
        return state_now
    '''
    execute_action函数就是通常所说的step函数
    流程： 
        输入动作：0-10架飞机进行巡逻
        执行动作：更新巡逻区
        更新态势
        获取观察
        获取reward
        检查是否结束
        如果最后收敛的情况下，会选择一个最好的起飞数量，并且保持不变        
    参数：无
    返回： 1）state：状态；
           2）reward：回报值
    '''
    def execute_action(self, action):
        super(feihaiblue, self).step()
        # nine_zone = self.train_zones
        print('action=', action)
        # final_patrol_ = self.point_list
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        # self.update_patrol_mission_zone(self.blueside, final_patrol_zone)
        # self.update_presection_zone(self.blueside, final_patrol_zone)
        
        # TODO ： 实现action，按照action将没有执行任务的飞机添加到编队中
        self.update_patrol_mission(action)

        # 动作下达了，该仿真程序运行，以便执行指令
        self.mozi_server.run_grpc_simulate()

        # 更新数据时，会被阻塞，实现与仿真的同步
        self._update()

        obs = self.get_observation()
        reward = self.get_reward()
        done = self.check_done()

        return np.array(obs), reward, done

    
    def update_patrol_mission(self,action):
        """ 
        设置当前起飞的飞机数量,与action + 1 数量一致 （action返回0~9，计算派出的飞机数量为1~10）
        """
        patrolmssn = list(self.blueside.get_patrol_missions().values())[0]
        assigned_aircrafts = list(patrolmssn.get_assigned_units().keys())
        unassigned_aircrafts = list(patrolmssn.get_unassigned_units().keys())
        print('上一次设置的飞机起飞数量',len(assigned_aircrafts))
        # action返回0~9，计算派出的飞机数量为 1~10
        action += 1
        if len(assigned_aircrafts) == action:
            pass
        elif len(assigned_aircrafts) > action:
            for i in range(len(assigned_aircrafts) - action ):
                patrolmssn.unassign_unit(assigned_aircrafts[i])
        elif len(assigned_aircrafts) < action :
            for i in range(action - len(assigned_aircrafts)):
                if len(unassigned_aircrafts) > i :
                    patrolmssn.assign_unit(unassigned_aircrafts[i])
                else:
                    pass

    def _update(self):
        """
        更新
        """
        # self.mozi_server.update_situation(self.scenario, self.app_mode)
        self.redside.static_update()
        self.blueside.static_update()
    def get_reward(self):
        """
        获取奖励，最终奖励设置原则是选择包含红方飞机最多的，且离蓝方飞机最近的格子
        """
        # blueside = self.scenario.get_side_by_name(self.blue_side_name)
        reward = 0.0
        # 发现的红方目标数量越多，奖励值越大
        num_reward = self._get_num_reward() 
        # 获取得分奖励，战损战果
        score_reward = float(self.blueside.iTotalScore) / 500
        print('得分奖励',score_reward)
        #获得油料奖励
        fuel_reward= self._get_fuel_reward()
        # 对2个reward 进行加权求和作为总reward
        reward =  num_reward +  score_reward +  fuel_reward
        print('总奖励', reward)
        return reward
    def _get_fuel_reward(self):
        #获取当前的平均剩余油量
        num = 0
        for k,v in self.blue_unit_dict_total.items() :
            num += v.iCurrentFuelQuantity
        num /= 10000
        print ('油料奖励', num / 10)
        return num

    def _get_num_reward(self):
        # 获得该区域内红方目标数量，数量越多，reward越大
        contact = self.blueside.contacts
        detection_rate = len(contact) / (len(self.red_unit_dict_total) + len(self.redside.ships))
        print('目标奖励',detection_rate * 10)
        return detection_rate * 10


    def check_done(self):
        # 判断是否结束，如果蓝方飞机都打没了，结束，红方飞机都打没了，结束，否则继续
        if len(self.blue_unit_dict_total) == 0 or len(self.red_unit_dict_total) == 0:
            return True
        else:
            return False
