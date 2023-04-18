# 时间 ： 2022/05/19
# 作者 ： zangzh
# 文件 ： bt_red_defence.py
# 项目 ： mozi
# 版权 ： ISCAS

from red_agent_zzh_v1.utils.bt_rd_leaf_nodes_eg import *
from mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class ZZHAgent:

    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None

    def init_bt(self, env, side_name, len_ai, options):
        side = env.scenario.get_side_by_name(side_name)
        side_guid = side.strGuid
        short_side_key = "a" + str(len_ai + 1)
        attributes = options

        # 行为树的节点
        hx_sequence = BT()
        warning_mission_select = BT()
        anti_air_mission_select = BT()

        warning_mission_condition = BT()
        update_warning_patrol_mission_bt = BT()
        create_warning_patrol_mission_bt = BT()

        anti_air_mission_condition = BT()
        update_anti_air_mission_bt = BT()
        create_anti_air_mission_bt = BT()

        hx_sequence.add_child(warning_mission_select)
        hx_sequence.add_child(anti_air_mission_select)

        warning_mission_select.add_child(warning_mission_condition)
        warning_mission_select.add_child(update_warning_patrol_mission_bt)
        warning_mission_select.add_child(create_warning_patrol_mission_bt)

        anti_air_mission_select.add_child(anti_air_mission_condition)
        anti_air_mission_select.add_child(update_anti_air_mission_bt)
        anti_air_mission_select.add_child(create_anti_air_mission_bt)

        hx_sequence.set_action(hx_sequence.sequence, side_guid, short_side_key,
                               attributes)

        warning_mission_select.set_action(warning_mission_select.select,
                                          side_guid, short_side_key,
                                          attributes)
        warning_mission_condition.set_action(warning_patrol_condition,
                                             side_guid, short_side_key,
                                             attributes)
        update_warning_patrol_mission_bt.set_action(
            update_warning_patrol_mission, side_guid, short_side_key,
            attributes)
        create_warning_patrol_mission_bt.set_action(
            create_warning_patrol_mission, side_guid, short_side_key,
            attributes)

        anti_air_mission_select.set_action(anti_air_mission_select.select,
                                           side_guid, short_side_key,
                                           attributes)
        anti_air_mission_condition.set_action(anti_air_condition, side_guid,
                                              short_side_key, attributes)
        update_anti_air_mission_bt.set_action(update_anti_air_mission,
                                              side_guid, short_side_key,
                                              attributes)
        create_anti_air_mission_bt.set_action(create_anti_air_mission,
                                              side_guid, short_side_key,
                                              attributes)

        self.bt = hx_sequence

    # 更新行为树
    def update_bt(self, side_name, scenario):
        return self.bt.run(side_name, scenario)

    def test(self, side_name, scenario):
        create_warning_patrol_mission(side_name, scenario)
