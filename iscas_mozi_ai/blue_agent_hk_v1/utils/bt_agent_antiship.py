# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： bt_agent_antiship.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from mozi_ai_sdk.rule_bot.utils.agent import update
from mozi_simu_sdk import mission
from mozi_ai_sdk.btmodel import bt
# from mozi_ai_sdk.blue_test.utils.leaf_nodes_eg import *
from blue_agent_hk_v1.utils.leaf_1 import *
from mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class CAgent:

    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None

    # def init_bt(self, env, side_name, lenAI, options):
    #     side = env.scenario.get_side_by_name(side_name)
    #     sideGuid = side.strGuid
    #     shortSideKey = "a" + str(lenAI + 1)
    #     attributes = options
    #     # 行为树的节点
    #     hxSequence = BT()
    #     missionSelector = BT()
    #     missionSelectorCondition = BT()
    #     patrolMissionSelector = BT()
    #     createPatrolMission = BT()
    #     updatePatrolMission = BT()

    #     # 反舰节点
    #     AntiSurfaceShipMissionSelector = BT()
    #     CreateAntiSurfaceShipMission = BT()
    #     UpdateAntiSurfaceShipMission = BT()

    #     # 连接节点形成树
    #     hxSequence.add_child(missionSelector)
    #     hxSequence.add_child(AntiSurfaceShipMissionSelector)
    #     missionSelector.add_child(missionSelectorCondition)
    #     missionSelector.add_child(patrolMissionSelector)

    #     patrolMissionSelector.add_child(updatePatrolMission)
    #     patrolMissionSelector.add_child(createPatrolMission)

    #     AntiSurfaceShipMissionSelector.add_child(CreateAntiSurfaceShipMission)
    #     AntiSurfaceShipMissionSelector.add_child(UpdateAntiSurfaceShipMission)

    #     # 每个节点执行的动作
    #     hxSequence.set_action(hxSequence.sequence,
    #                           sideGuid, shortSideKey, attributes)
    #     missionSelector.set_action(
    #         missionSelector.select, sideGuid, shortSideKey, attributes)
    #     missionSelectorCondition.set_action(
    #         antiship_condition_check, sideGuid, shortSideKey, attributes)

    #     patrolMissionSelector.set_action(
    #         patrolMissionSelector.select, sideGuid, shortSideKey, attributes)

    #     updatePatrolMission.set_action(
    #         update_patrol_mission, sideGuid, shortSideKey, attributes)
    #     createPatrolMission.set_action(
    #         create_patrol_mission, sideGuid, shortSideKey, attributes)

    #     AntiSurfaceShipMissionSelector.set_action(AntiSurfaceShipMissionSelector.select, sideGuid, shortSideKey,
    #                                               attributes)
    #     CreateAntiSurfaceShipMission.set_action(
    #         create_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
    #     UpdateAntiSurfaceShipMission.set_action(
    #         update_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
    #     self.bt = hxSequence

    # 更新行为树
    def update_bt(self, side_name, scenario):
        return self.bt.run(side_name, scenario)

    # 首次尝试行为树编写
    def my_act_tree(self, env, side_name, lenAI, options):
        side = env.scenario.get_side_by_name(side_name)
        sideGuid = side.strGuid
        shortSideKey = "a" + str(lenAI + 1)
        attributes = options

        # 创建行为树
        # 干扰、侦察、对空作战、反舰
        # 初次创建预警任务，打开雷达
        hxSequence = BT()
        missionSelector = BT()

        # 预警节点
        missionYJ = BT()
        createMissionYJ = BT()
        updateMissionYJ = BT()

        # 打击节点
        attackShip = BT()
        createMissionAtt = BT()
        updateMissionAtt = BT()

        # 连接节点
        hxSequence.add_child(missionSelector)
        missionSelector.add_child(missionYJ)
        missionYJ.add_child(createMissionYJ)
        missionYJ.add_child(updateMissionYJ)

        hxSequence.add_child(attackShip)
        attackShip.add_child(createMissionAtt)
        attackShip.add_child(updateMissionAtt)

        # 设置动作
        # 每个节点执行的动作
        # hxSequence.set_action(hxSequence.sequence,
        #                       sideGuid, shortSideKey, attributes)
        hxSequence.set_action(hxSequence.select, sideGuid, shortSideKey,
                              attributes)
        missionSelector.set_action(missionSelector.select, sideGuid,
                                   shortSideKey, attributes)
        missionYJ.set_action(missionYJ.select, sideGuid, shortSideKey,
                             attributes)
        createMissionYJ.set_action(create_patrol_mission, sideGuid,
                                   shortSideKey, attributes)
        updateMissionYJ.set_action(update_patrol_mission, sideGuid,
                                   shortSideKey, attributes)

        attackShip.set_action(attackShip.select, sideGuid, shortSideKey,
                              attributes)
        createMissionAtt.set_action(create_att_ship, sideGuid, shortSideKey,
                                    attributes)
        updateMissionAtt.set_action(update_att_ship, sideGuid, shortSideKey,
                                    attributes)
        self.bt = hxSequence
