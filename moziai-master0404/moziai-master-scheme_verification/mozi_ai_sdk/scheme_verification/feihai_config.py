# 任务类型（mission_type），指令类型（order_type）对照表



class MISSION_TYPE:
    AIR_STRIKE = 1 # 对空打击
    LAND_STRIKE = 2 # 对陆打击
    SEA_STRIKE = 3 # 对海打击
    SUB_STRIKE = 4 # 对潜打击
    AIR_PATROL = 5 # 空战巡逻
    ANTI_SEA_PATROL = 6 # 反水面战巡逻
    ANTI_LAND_PATROL = 7 # 反地面战巡逻
    ANTI_LAND_SEA_PATROL = 8 # 反地面水面战巡逻
    ANTI_SUB_PATROL = 9 # 反潜巡逻
    SUPPORT = 10 # 支援

class ORDER_TYPE:
    ADD_AIR_STRIKE_ORDER = 1 # 创建对空打击指令
    ADD_LAND_STRIKE_ORDER = 2  # 创建对陆打击指令
    ADD_SEA_STRIKE_ORDER = 3 # 创建对海打击指令
    ADD_SUB_STRIKE_ORDER = 4 # 创建对潜打击指令
    ADD_AIR_PATROL_ORDER = 5 # 创建空战巡逻指令
    ADD_ANTI_SEA_PATROL_ORDER = 6 # 创建反水面战巡逻指令
    ADD_ANTI_LAND_PATROL = 7 # 创建反地面战巡逻指令
    ADD_ANTI_LAND_SEA_PATROL = 8 # 创建反地面水面战巡逻指令
    ADD_ANTI_SUB_PATROL_ORDER = 9 # 创建反潜巡逻指令
    ADD_SUPPORT_ORDER = 10 # 创建支援指令
    UPDATE_REFENCE_POINT = 11 # 更新参考点指令
    CHANGE_ORDER = 12 # 更换指令

# a = ORDER_TYPE
# b= a.UPDATE_REFENCE_POINT
# print(ORDER_TYPE.CHANGE_ORDER)