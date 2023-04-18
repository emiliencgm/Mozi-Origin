
from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestContact(TestFramework):
    """测试探测目标"""

    def test_get_type_description(self):
        """获取探测目标的类型描述"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        info = contact.get_type_description()
        self.env.step()
        self.assertEqual(info, 'Air')

    def test_get_contact_info(self):
        """获取目标信息字典"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        info = contact.get_contact_info()
        self.env.step()

    def test_get_actual_unit(self):
        """获取目标真实单元"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        info = contact.get_actual_unit()
        self.env.step()
        self.assertEqual(info.strName, '敌机1')

    def test_get_original_detector_side(self):
        """获取探测到单元的方"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        info = contact.get_original_detector_side()
        self.env.step()
        self.assertEqual(info.strName, '红方')

    def test_get_original_target_side(self):
        """获取目标单元所在方"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        info = contact.get_original_target_side()
        self.env.step()
        self.assertEqual(info.strName, '蓝方')

    def test_set_mark_contact(self):
        """标识目标立场"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        # 'F'：友方，'N'：中立，'U'：非友方，'H'：敌方
        contact.set_mark_contact('F')
        self.env.step()
        contact.set_mark_contact('N')
        self.env.step()
        contact.set_mark_contact('U')
        self.env.step()
        contact.set_mark_contact('H')
        self.env.step()

    def test_hs_contact_rename(self):
        """重命名目标"""
        # 获取所有探测目标
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        # 将目标重命名为'敌机1'
        contact.hs_contact_rename('敌机1')
        self.env.step()

    def test_hs_contact_drop_target(self):
        """放弃目标"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        # 放弃目标
        contact.hs_contact_drop_target()
        self.env.step()

    def test_hs_contact_filter_target(self):
        """过滤目标"""
        contact = self.red_side.get_contacts()[self.enemy_airplane_guid]
        # 过滤目标
        contact.hs_contact_drop_target()
        self.env.step()

