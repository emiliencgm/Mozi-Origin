# 时间 : 2021/08/24 16:35
# 作者 : 张志高
# 文件 : patrol_mission
# 项目 : 墨子联合作战智能体研发平台
# 版权 : 北京华戍防务技术有限公司

from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestPatrolMission(TestFramework):
    """测试巡逻任务类"""

    def test_set_prosecution_zone(self):
        """设置巡逻任务的警戒区"""
        point_list = ['RP-74', 'RP-75', 'RP-76', 'RP-77']
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_prosecution_zone(point_list)
        point_list = ['RP-74', 'RP-75', 'RP-76']
        mission.set_prosecution_zone(point_list)
        self.env.step()

    def test_set_patrol_zone(self):
        """设置巡逻任务的巡逻区"""
        point_list = ['RP-74', 'RP-76', 'RP-77']
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_patrol_zone(point_list)
        point_list = ['RP-74', 'RP-75', 'RP-76']
        mission.set_patrol_zone(point_list)
        self.env.step()

    def test_assign_unit(self):
        """分配单元"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.assign_unit(self.antisubmarine_aircraft_guid)
        self.env.step()

    def test_get_doctrine(self):
        """获取任务条令"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        doctrine = mission.get_doctrine()
        self.assertEqual(doctrine.m_DoctrineOwner, mission.strGuid)

        # 设置对空限制开火
        doctrine.set_weapon_control_status('weapon_control_status_air', 2)
        self.env.step()
        self.assertEqual(2, doctrine.m_WCS_Air)

    def test_set_is_active(self):
        """设置是否启用任务"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_is_active('true')
        self.env.step()
        self.assertEqual(0, mission.m_MissionStatus)
        mission.set_is_active('false')
        self.env.step()
        self.assertEqual(1, mission.m_MissionStatus)

    def test_set_time(self):
        """设置任务时间"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_start_time('2021-07-19 22:10:00')
        mission.set_end_time('2021-07-19 23:10:00')
        self.env.step()

    def test_set_maintain_unit_number(self):
        """巡逻任务阵位上每类平台保存作战单元数量"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 阵位上没类平台保持2个单元
        mission.set_maintain_unit_number(2)
        self.env.step()

    def test_set_opa_check(self):
        """设置任务是否对巡逻区外的探测目标进行分析"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_opa_check('false')
        self.env.step()
        mission.set_opa_check('true')
        self.env.step()

    def test_set_emcon_usage(self):
        """设置任务是否仅在巡逻/警戒区内打开电磁辐射"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_emcon_usage('true')
        self.env.step()
        mission.set_emcon_usage('false')
        self.env.step()

    def test_set_wwr_check(self):
        """设置任务是否对武器射程内探测目标进行分析"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_wwr_check('false')
        self.env.step()
        mission.set_wwr_check('true')
        self.env.step()

    def test_set_flight_size(self):
        """设置打击任务编队规模"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_flight_size(1)
        self.env.step()
        mission.set_flight_size(2)
        self.env.step()
        mission.set_flight_size(3)
        self.env.step()
        mission.set_flight_size(4)
        self.env.step()
        mission.set_flight_size(6)
        self.env.step()
        # TODO， 列表中没有all选项
        mission.set_flight_size('all')
        self.env.step()

    def test_set_flight_size(self):
        """设置打击任务是否飞机数低于编组规模数要求就不能起飞"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_flight_size_check('true')
        self.env.step()
        mission.set_flight_size_check('false')
        self.env.step()

    def test_set_throttle(self):
        """设置任务的油门"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 出航-巡航
        mission.set_throttle_transit('Cruise')
        # 阵位 - 军用
        mission.set_throttle_station('Full')
        # 攻击 - 加力
        mission.set_throttle_attack('Flank')
        self.env.step()

    def test_set_throttle_ship(self):
        """设置任务的水面舰艇油门"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 出航-巡航
        mission.set_throttle_transit_ship('Cruise')
        # 阵位 - 全速
        mission.set_throttle_station_ship('Full')
        # 攻击 - 最大
        mission.set_throttle_attack_ship('Flank')
        self.env.step()

    def test_set_altitude(self):
        """设置任务的出航/阵位/攻击高度"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 出航高度
        mission.set_transit_altitude(1000)
        self.env.step()
        # 阵位高度
        mission.set_station_altitude(2000)
        self.env.step()
        # 攻击高度
        mission.set_attack_altitude(3000)
        self.env.step()

    def test_set_attack_distance(self):
        """设置任务的攻击距离"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 攻击距离
        mission.set_attack_distance(500)
        self.env.step()

    def test_set_patrol_sonobuoys_cover(self):
        """反潜巡逻任务设置声呐浮标在巡逻区域内的覆盖密度和深浅类型"""
        # 反潜巡逻
        point_list = ['RP-74', 'RP-75', 'RP-76', 'RP-77']
        mission = self.red_side.add_mission_patrol('反潜巡逻', 4, point_list)
        # 投放声呐覆盖3倍半径，声呐浮标深度温跃层之下
        mission.set_patrol_sonobuoys_cover(3.0, 2)
        self.env.step()

    def test_add_plan_way_to_mission(self):
        """为任务分配预设航线"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        self.red_side.add_plan_way(0, '单元航线-新')
        # 出航航线
        mission.add_plan_way_to_mission(0, '单元航线-新')
        # 返航航线
        mission.add_plan_way_to_mission(2, '单元航线-新')
        # 巡逻航线
        mission.add_plan_way_to_mission(3, '单元航线-新')
        self.env.step()

    def test_set_flight_size(self):
        """飞机编队规模"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_flight_size(4)
        self.env.step()

    def test_set_use_refuel_unrep(self):
        """空中加油"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 不允许加油
        mission.set_use_refuel_unrep(1)
        self.env.step()
        # 允许
        mission.set_use_refuel_unrep(2)
        self.env.step()
        # 0--允许但不允许给加油机加油
        mission.set_use_refuel_unrep(0)
        self.env.step()

    def test_set_group_size(self):
        """设置巡逻任务水面舰艇/潜艇编队规模"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.set_group_size(6)
        self.env.step()
        # 查看墨子， 空中巡逻任务水面舰艇/潜艇编队规模为6x艇


if __name__ == '__main__':
    TestPatrolMission.main()


