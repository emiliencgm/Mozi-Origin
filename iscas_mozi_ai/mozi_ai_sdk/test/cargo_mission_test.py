# 时间 : 2021/09/06 17:10
# 作者 : 张志高
# 文件 : cargo_mission_test
# 项目 : 墨子联合作战智能体研发平台
# 版权 : 北京华戍防务技术有限公司

from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestCargoMission(TestFramework):
    """测试投送任务类"""

    def test_add_remove_mount_to_unload(self):
        """设置投送任务的货物加1减1"""
        # TODO 更新态势后, 货物消失
        mission = self.red_side.get_missions_by_name('投送')
        mission.add_mount_to_unload('hsfw-datamount-000000000002322')
        self.env.step()
        mission.remove_mount_to_unload('hsfw-datamount-000000000002322')
        self.env.step()

    def test_set_zone(self):
        mission = self.red_side.get_missions_by_name('投送')
        point_list = ['RP-74', 'RP-76', 'RP-77']
        mission.set_zone(point_list)
        self.env.step()

    def test_get_doctrine(self):
        """获取任务条令"""
        mission = self.red_side.get_missions_by_name('投送')
        doctrine = mission.get_doctrine()
        self.assertEqual(doctrine.m_DoctrineOwner, mission.strGuid)

        # 设置对空限制开火
        doctrine.set_weapon_control_status('weapon_control_status_air', 2)
        self.env.step()
        self.assertEqual(2, doctrine.m_WCS_Air)

    def test_set_is_active(self):
        """设置是否启用任务"""
        mission = self.red_side.get_missions_by_name('投送')
        mission.set_is_active('true')
        self.env.step()
        self.assertEqual(0, mission.m_MissionStatus)
        mission.set_is_active('false')
        self.env.step()
        self.assertEqual(1, mission.m_MissionStatus)

    def test_set_time(self):
        """设置任务时间"""
        mission = self.red_side.get_missions_by_name('投送')
        mission.set_start_time('2021-07-19 22:10:00')
        mission.set_end_time('2021-07-19 23:10:00')
        self.env.step()

    def test_set_throttle_altitude(self):
        """设置任务的油门高度"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('投送')
        # 出航油门-巡航
        mission.set_throttle_transit('Cruise')
        # 阵位油门-军用
        mission.set_throttle_station('Full')
        # 出航高度
        mission.set_transit_altitude(1000)
        # 阵位高度
        mission.set_station_altitude(2000)
        self.env.step()

    def test_add_plan_way_to_mission(self):
        """为任务分配预设航线"""
        mission = self.red_side.get_missions_by_name('投送')
        self.red_side.add_plan_way(0, '单元航线-新')
        # 出航航线 TODO 不起作用
        mission.add_plan_way_to_mission(0, '单元航线-新')
        self.env.step()

    def test_set_throttle_ship(self):
        """设置任务的水面舰艇油门"""
        # 空战巡逻
        mission = self.red_side.get_missions_by_name('投送')
        # 出航-巡航
        mission.set_throttle_transit_ship('Cruise')
        # 阵位 - 全速
        mission.set_throttle_station_ship('Full')
        self.env.step()

