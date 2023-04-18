# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： bt_agent_antiship.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from mozi_ai_sdk.feihai_blue.utils.leaf_nodes_eg import *
from mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class CAgent:
    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None

    def init_bt(self, env, side_name, lenAI, options):
        # side是个对象
        # options=''
        side = env.scenario.get_side_by_name(side_name)
        sideGuid = side.strGuid
        shortSideKey = "a" + str(lenAI + 1)
        attributes = options
        # 行为树的节点
        # f16_group_sequence是根节点
        f16_group_sequence = BT()
        # 任务选择节点
        edit_leaf = BT()
        # 任务选择条件
        check_sequence = BT()
        # 任务选择
        unit_and_mission_leaf = BT()
        # 创建空战任务
        air_combat_leaf = BT()

        # 连接节点形成树
        f16_group_sequence.add_child(edit_leaf)
        f16_group_sequence.add_child(check_sequence)
        check_sequence.add_child(unit_and_mission_leaf)
        check_sequence.add_child(air_combat_leaf)

        # 每个节点执行的动作
        f16_group_sequence.set_action(f16_group_sequence.sequence, sideGuid, shortSideKey, attributes)
        edit_leaf.set_action(edit, sideGuid, shortSideKey, attributes)
        check_sequence.set_action(check_sequence.sequence, sideGuid, shortSideKey, attributes)

        unit_and_mission_leaf.set_action(unit_and_mission, sideGuid, shortSideKey, attributes)

        air_combat_leaf.set_action(air_combat, sideGuid, shortSideKey, attributes)
        self.bt = f16_group_sequence

    # 更新行为树
    def update_bt(self, side_name, scenario):
        # self.bt.run=action,action=hxSequence.sequence等
        return self.bt.run(side_name, scenario)
