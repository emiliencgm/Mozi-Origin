from mozi_ai_sdk.test.utils.test_framework import TestFramework


class TestMagazine(TestFramework):
    """测试弹药库"""

    def test_set_magazine_state(self):
        """设置弹药库状态"""
        magazines = self.ground_to_air_missile_squadron.get_magazines()

        magazine = None
        for k, v in magazines.items():
            if v.strName == '“毒刺”肩射地空导弹':
                magazine = v
                break
        # 设置弹药库状态为已被摧毁
        magazine.set_magazine_state('摧毁')
        self.env.step()

    def test_remove_weapon(self):
        """设置弹药库状态"""
        magazines = self.ground_to_air_missile_squadron.get_magazines()

        magazine = None
        for k, v in magazines.items():
            if v.strName == '“毒刺”肩射地空导弹':
                magazine = v
                break
        # 设置弹药库状态为已被摧毁
        weapon_guid = v.m_LoadRatio.split('$')[0]
        magazine.remove_weapon(weapon_guid)
        self.env.step()
