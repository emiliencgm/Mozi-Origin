# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： bt_agent_antiship.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from red_agent_lk_v1.utils_v1.leaf_nodes_eg import *
from mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class CAgent:

    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None

    def init_bt(self, env, side_name, lenAI, options):
        side = env.scenario.get_side_by_name(side_name)
        sideGuid = side.strGuid
        shortSideKey = "a" + str(lenAI + 1)
        attributes = options
        # 行为树的节点
        hxSequence = BT()
        missionSelector = BT()
        missionSelectorCondition = BT()
        patrolMissionSelector = BT()

        createPatrolMission = BT()
        updatePatrolMission = BT()

        # 空中截击
        AirAttackMissionSelector = BT()
        CreateAirAttackMission = BT()
        UpdateAirAttackMission = BT()

        # 连接节点形成树
        hxSequence.add_child(missionSelector)
        hxSequence.add_child(AirAttackMissionSelector)
        missionSelector.add_child(missionSelectorCondition)
        missionSelector.add_child(patrolMissionSelector)

        patrolMissionSelector.add_child(updatePatrolMission)
        patrolMissionSelector.add_child(createPatrolMission)

        AirAttackMissionSelector.add_child(CreateAirAttackMission)
        AirAttackMissionSelector.add_child(UpdateAirAttackMission)

        # 每个节点执行的动作
        hxSequence.set_action(hxSequence.sequence, sideGuid, shortSideKey,
                              attributes)
        missionSelector.set_action(missionSelector.select, sideGuid,
                                   shortSideKey, attributes)

        missionSelectorCondition.set_action(attack_condition_check, sideGuid,
                                            shortSideKey, attributes)

        patrolMissionSelector.set_action(patrolMissionSelector.select,
                                         sideGuid, shortSideKey, attributes)
        updatePatrolMission.set_action(update_patrol_mission_v2, sideGuid,
                                       shortSideKey, attributes)
        createPatrolMission.set_action(create_patrol_mission, sideGuid,
                                       shortSideKey, attributes)

        AirAttackMissionSelector.set_action(AirAttackMissionSelector.select,
                                            sideGuid, shortSideKey, attributes)
        CreateAirAttackMission.set_action(create_air_attack, sideGuid,
                                          shortSideKey, attributes)
        UpdateAirAttackMission.set_action(update_air_attack, sideGuid,
                                          shortSideKey, attributes)
        self.bt = hxSequence

    # 更新行为树
    def update_bt(self, side_name, scenario):
        return self.bt.run(side_name, scenario)
