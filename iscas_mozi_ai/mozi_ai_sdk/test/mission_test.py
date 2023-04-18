# 时间 : 2021/08/09 17:12
# 作者 : 张志高
# 文件 : mission_test
# 项目 : 墨子联合作战智能体研发平台
# 版权 : 北京华戍防务技术有限公司

from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestMission(TestFramework):
    """测试任务类"""

    def test_get_assigned_units(self):
        """获取已分配任务的单元"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        units = mission_fuel.get_assigned_units()
        for k, v in units.items():
            self.assertEqual(v.strName, '飞行编队 59')

    def test_get_unassigned_units(self):
        """获取未分配任务的单元"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        units = mission_fuel.get_unassigned_units()
        flag_1 = False
        flag_2 = False
        for k, v in units.items():
            if v.strName == '反潜机1':
                flag_1 = True
            if v.strName == '飞行编队 59':
                flag_1 = True
        self.assertTrue(flag_1)
        self.assertFalse(flag_2)

    def test_get_doctrine(self):
        """获取任务条令"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        doctrine = mission_fuel.get_doctrine()
        self.assertEqual(doctrine.m_DoctrineOwner, mission_fuel.strGuid)

    def test_get_weapon_db_guids(self):
        """获取编组内所有武器的数据库guid"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        self.antisubmarine_aircraft.assign_unit_to_mission('加油任务')
        self.env.step()
        weapon_db_guids = mission_fuel.get_weapon_db_guids()
        print(123)

    def test_get_weapon_infos(self):
        """获取编组内所有武器的名称及db_guid"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        self.antisubmarine_aircraft.assign_unit_to_mission('加油任务')
        self.env.step()
        weapon_infos = mission_fuel.get_weapon_infos()
        print(123)

    def test_get_side(self):
        """获取任务所在方"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        side = mission_fuel.get_side()
        self.assertEqual(side, self.red_side)

    def test_set_is_active(self):
        """设置是否启用任务"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        mission_fuel.set_is_active('false')
        self.env.step()

    def test_set_start_time(self):
        """设置任务开始时间"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        mission_fuel.set_start_time('2021-07-19 22:10:00')
        self.env.step()

    def test_set_end_time(self):
        """设置任务结束时间"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        mission_fuel.set_end_time('2021-07-19 22:10:00')
        self.env.step()

    def test_set_one_third_rule(self):
        """设置任务是否遵循1/3原则"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        mission_fuel.set_one_third_rule('false')
        self.env.step()

    def test_switch_radar(self):
        """设置任务雷达是否打开"""
        mission_fuel = self.red_side.get_missions_by_name('加油任务')
        mission_fuel.switch_radar(True)
        self.env.step()
        # 任务条令中，雷达为打开

    def test_assign_unit(self):
        """分配单元"""
        mission = self.red_side.get_missions_by_name('空中打击')
        mission.assign_unit(self.antisubmarine_aircraft_guid)
        mission.assign_unit(self.antisubmarine_aircraft_2_guid, True)
        self.env.step()

    def test_assign_units(self):
        """分配多个单元"""
        mission = self.red_side.get_missions_by_name('空中打击')
        mission.assign_units({self.antisubmarine_aircraft_guid: self.antisubmarine_aircraft,
                              self.antisubmarine_aircraft_2_guid: self.antisubmarine_aircraft_2})
        self.env.step()

    def test_get_information(self):
        # TODO 不可用，考虑删除
        mission = self.red_side.get_missions_by_name('空中打击')
        info = mission.get_information()
        self.env.step()

    def test_is_area_valid(self):
        """验证区域角点连线是否存在交叉现象"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        info = mission.is_area_valid()
        self.assertEqual(info, "Yes")

    def test_unassign_unit(self):
        """单元从任务中移除"""
        mission = self.red_side.get_missions_by_name('加油任务')
        mission.unassign_unit(self.refueling_tanker_aircraft_guid)
        self.env.step()

    def test_export_mission(self):
        """相应的任务导出到 Defaults 文件夹中"""
        mission = self.red_side.get_missions_by_name('加油任务')
        mission.export_mission()
        self.env.step()

    def test_set_throttle(self):
        """设置任务油门类型及值"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 出航油门 - 低速
        mission.set_throttle('transitThrottleAircraft', 'Loiter')
        # 阵位油门 - 巡航
        mission.set_throttle('stationThrottleAircraft', 'Cruise')
        # 攻击油门 - 军用
        mission.set_throttle('attackThrottleAircraft', 'Full')
        self.env.step()

    def test_set_altitude(self):
        """设置任务高度类型及值"""
        mission = self.red_side.get_missions_by_name('空中巡逻')
        # 出航高度
        mission.set_altitude('transitAltitudeAircraft', 1000)
        # 阵位高度
        mission.set_altitude('stationAltitudeAircraft', 2000)
        # 攻击高度
        mission.set_altitude('attackAltitudeAircraft', 3000)
        self.env.step()

    def test_add_plan_way_to_mission(self):
        """为任务分配预设航线"""
        self.red_side.add_plan_way(0, '单元航线-新')
        self.red_side.add_plan_way(1, '武器航线-新')
        self.env.step()

        mission = self.red_side.get_missions_by_name('空中打击')
        mission.add_plan_way_to_mission(0, '单元航线-新')
        mission.add_plan_way_to_mission(1, '武器航线-新')
        self.env.step()

        mission = self.red_side.get_missions_by_name('空中巡逻')
        mission.add_plan_way_to_mission(2, '单元航线-新')
        mission.add_plan_way_to_mission(3, '单元航线-新')
        self.env.step()

    def test_add_plan_way_to_target(self):
        """武器打击目标预设航线"""
        self.red_side.add_plan_way(1, '武器航线-新')
        self.env.step()

        mission = self.red_side.get_missions_by_name('空中打击')
        mission.add_plan_way_to_target('武器航线-新', self.enemy_airplane_guid)
        self.env.step()


if __name__ == '__main__':
    TestMission.main()















