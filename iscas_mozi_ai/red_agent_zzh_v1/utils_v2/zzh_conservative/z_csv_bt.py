# 时间 ： 2022/05/19
# 作者 ： zangzh
# 文件 ： z_ags_bt.py
# 项目 ： mozi
# 版权 ： ISCAS

from .z_csv_leaf_nodes import *
from mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class ZConservativeAgent:
    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None
        self.ship_enabled = False

    def init_bt(self, env, side_name, len_ai, options):
        side = env.scenario.get_side_by_name(side_name)
        side_guid = side.strGuid
        short_side_key = "a" + str(len_ai + 1)
        attributes = options
        # 行为树的节点
        hx_sequence = BT()
        warning_mission_select = BT()
        air_defense_mission_select = BT()

        warning_mission_condition = BT()
        update_warning_patrol_mission_bt = BT()
        create_warning_patrol_mission_bt = BT()

        air_defense_mission_condition = BT()
        update_air_defense_mission_bt = BT()
        create_air_defense_mission_bt = BT()

        hx_sequence.add_child(warning_mission_select)
        hx_sequence.add_child(air_defense_mission_select)

        warning_mission_select.add_child(warning_mission_condition)
        warning_mission_select.add_child(update_warning_patrol_mission_bt)
        warning_mission_select.add_child(create_warning_patrol_mission_bt)

        air_defense_mission_select.add_child(air_defense_mission_condition)
        air_defense_mission_select.add_child(update_air_defense_mission_bt)
        air_defense_mission_select.add_child(create_air_defense_mission_bt)

        hx_sequence.set_action(hx_sequence.sequence, side_guid, short_side_key, attributes)

        warning_mission_select.set_action(warning_mission_select.select, side_guid, short_side_key, attributes)
        warning_mission_condition.set_action(warning_patrol_condition, side_guid, short_side_key, attributes)
        update_warning_patrol_mission_bt.set_action(update_warning_patrol_mission, side_guid, short_side_key, attributes)
        create_warning_patrol_mission_bt.set_action(create_warning_patrol_mission, side_guid, short_side_key, attributes)

        air_defense_mission_select.set_action(air_defense_mission_select.select, side_guid, short_side_key, attributes)
        air_defense_mission_condition.set_action(air_defense_condition, side_guid, short_side_key, attributes)
        update_air_defense_mission_bt.set_action(update_air_defense_mission, side_guid, short_side_key, attributes)
        create_air_defense_mission_bt.set_action(create_air_defense_mission, side_guid, short_side_key, attributes)

        self.bt = hx_sequence

    # 更新行为树
    def update_bt(self, side_name, scenario):
        if not self.ship_enabled:
            print("舰船激活")
            create_ship_mission(side_name, scenario)
            self.ship_enabled = True
        return self.bt.run(side_name, scenario)

