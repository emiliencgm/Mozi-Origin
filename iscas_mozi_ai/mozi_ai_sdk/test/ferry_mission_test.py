# 时间 : 2021/09/08 15:30
# 作者 : 张志高
# 文件 : ferry_mission_test
# 项目 : 墨子联合作战智能体研发平台
# 版权 : 北京华戍防务技术有限公司

from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestFerryMission(TestFramework):
    """测试转场任务类"""

    def test_add_plan_way_to_mission(self):
        """为任务分配预设航线"""
        self.red_side.add_plan_way(0, '单元航线-新')
        mission = self.red_side.get_missions_by_name('转场')
        # 出航航线
        mission.add_plan_way_to_mission(0, '单元航线-新')
        self.env.step()

    def test_set_ferry_behavior(self):
        mission = self.red_side.get_missions_by_name('转场')
        mission.set_ferry_behavior('Cycle')
        mission.set_ferry_behavior('OneWay')
        mission.set_ferry_behavior('Random')
        self.env.step()

    def test_get_doctrine(self):
        """获取任务条令"""
        mission = self.red_side.get_missions_by_name('转场')
        doctrine = mission.get_doctrine()
        self.assertEqual(doctrine.m_DoctrineOwner, mission.strGuid)

        # 设置对空限制开火
        doctrine.set_weapon_control_status('weapon_control_status_air', 2)
        self.env.step()
        self.assertEqual(2, doctrine.m_WCS_Air)

    def test_set_is_active(self):
        """设置是否启用任务"""
        mission = self.red_side.get_missions_by_name('转场')
        mission.set_is_active('true')
        self.env.step()
        self.assertEqual(0, mission.m_MissionStatus)
        mission.set_is_active('false')
        self.env.step()
        self.assertEqual(1, mission.m_MissionStatus)

    def test_set_time(self):
        """设置任务时间"""
        mission = self.red_side.get_missions_by_name('转场')
        mission.set_start_time('2021-07-19 22:10:00')
        mission.set_end_time('2021-07-19 23:10:00')
        self.env.step()

    def test_set_ferry_throttle_altitude(self):
        """设置转场任务油门和高度"""
        mission = self.red_side.get_missions_by_name('转场')
        # 军用
        mission.set_ferry_throttle_aircraft('Full')
        mission.set_ferry_altitude_aircraft(6000.1)
        self.env.step()

