# 时间 ： 2023/5/10 08:55
# 作者 ： CGM
# 文件 ： garph_main.py
# 项目 ： mozi_graph_representation
# 版权 ： 
import numpy as np


class Graph_Construct:
    '''
    将墨子态势side转换为图数据:
    节点与实体之间的映射
    节点的属性
    节点之间的边
    边的属性
    '''
    def __init__(self, side_self, args, side_ops=None):
        #我方CSide类实例
        self.side_self = side_self
        #敌方CSide类实例
        self.side_ops = side_ops
        #图表示部分的参数
        self.args = args
        #目前版本选择的节点类型
        self.admissible_node_type = ['aircrafts', 'facilities', 'ships', 'submarines', 'weapons', 'satellites']
        #节点信息储存，尚不能保证同一索引代表的实体不会变化 —— 需要在使用时单独处理实体与节点索引的对应关系
        self.nodes_list, self.nodes_guid_list, self.nodes_attr_list, self.edges_index_list = [], [], [], [[],[]]
        #存储敌方信息
        self.nodes_list_ops, self.nodes_guid_list_ops, self.nodes_attr_list_ops, self.edges_index_list_ops = [], [], [], [[],[]]
        #通用的节点属性1——属性值为1维
        self.attr_vector_list_all_1 = ['side','ClassName', 'strName', 'm_ProficiencyLevel', 'dLatitude', 'dLongitude', 'fAltitude_AGL',
                                    'iAltitude_ASL', 'fCurrentHeading', 'fCurrentSpeed', 'm_CurrentThrottle', 'bAutoDetectable', 
                                    'strActiveUnitStatus', 'dFuelPercentage', 'strDamageState']
        #通用的节点属性2——属性值为多维，需要解析为1维的值
        self.attr_vector_list_all_2 = ['get_mounts()', 'get_ai_targets()', 'get_loadout()', 'get_sensor()', 'get_weapon_infos()']
        #飞机节点专有的属性(yaw==heading, 故不重复表示)
        self.attr_vector_list_aircrafts = ['strFuelState', 'fPitch', 'fRoll', 'iCurrentFuelQuantity']
        #设施节点专有的属性
        self.attr_vector_list_facilities = []
        #舰船节点专有的属性
        self.attr_vector_list_ships = []
        #潜艇节点专有的属性
        self.attr_vector_list_submarines = []
        #武器节点专有的属性
        self.attr_vector_list_weapons = []
        #卫星节点专有的属性
        self.attr_vector_list_satellites = []
        #每种类型的属性一共有多少
        self.attr_dim_list = [len(self.attr_vector_list_all_1), len(self.attr_vector_list_all_2), len(self.attr_vector_list_aircrafts), 
                            len(self.attr_vector_list_facilities), len(self.attr_vector_list_ships), len(self.attr_vector_list_submarines),
                            len(self.attr_vector_list_weapons), len(self.attr_vector_list_satellites)]
        #全部属性的数量——属性向量的总维度
        self.attr_dim = sum(self.attr_dim_list)
        #允许的边的类型
        self.admissible_edge_type = ['m_CurrentHostUnit(facility-->aircraft)', 'm_FiringUnitGuid(unit-->weapon)', 'm_PrimaryTargetGuid(weapon-->target)']
        #对admissible_edge_type的缩写，方便表示在可视化图中
        self.edge_type = ['host', 'fire', 'target']

    def identify_node(self):
        '''
        输入: 无
        输出: 实体节点列表(/字典), 实体guid列表, 实体节点对应的属性列表(/字典), 实体间边的两端节点索引
        '''
        #有选择地抽取side中的实体
        select_nodes_dict = {}
        for type, entities in self.side_self.__dict__.items():
            if type in self.admissible_node_type:
                select_nodes_dict[type] = entities
        #对敌方信息的处理
        select_nodes_dict_ops = {}
        for type, entities in self.side_ops.__dict__.items():
            if type in self.admissible_node_type:
                select_nodes_dict_ops[type] = entities
        
        #遍历每个实体以将其存储至节点信息列表
        #在每轮清空节点信息，重新开始搭建
        self.nodes_list = []
        self.nodes_list_ops = []
        self.nodes_guid_list = []
        self.nodes_guid_list_ops = []
        count_entity_node = 0
        for type, entity_dict in select_nodes_dict.items():
            for guid, entity in entity_dict.items():
                if guid not in self.nodes_guid_list:
                    self.nodes_guid_list.append(guid)
                    self.nodes_list.append(entity)

                count_entity_node += 1

        #对敌方信息处理
        for type, entity_dict in select_nodes_dict_ops.items():
            for guid, entity in entity_dict.items():
                if guid not in self.nodes_guid_list_ops:
                    if True:
                        self.nodes_guid_list_ops.append(guid)
                        self.nodes_list_ops.append(entity)
        
        #单独记录当前不可观测的敌方单位
        observed_ops_dict = self.side_self.contacts #Contacts == 观测到的敌方目标
        observed_ops_obj_list = []
        for contact_guid, contact_obj in observed_ops_dict.items():
            observed_ops_obj_list.append(contact_obj.get_actual_unit())
        self.unobserved_ops_list = []
        self.observed_ops_list = []
        for unit_ops in self.nodes_list_ops:
            if unit_ops not in observed_ops_obj_list:
                self.unobserved_ops_list.append(unit_ops)
            else:
                self.observed_ops_list.append(unit_ops)


        
        #将我方的实体和我方可观测的敌方实体整合起来，再统一进行属性整理、边的设置。
        self.num_nodes_self = len(self.nodes_list)#记录己方的实体数量，方便区分敌我
        self.nodes_list.extend(self.nodes_list_ops)
        self.nodes_guid_list.extend(self.nodes_guid_list_ops)


        #为每个实体整理属性向量
        self.nodes_attr_list = []
        for entity in self.nodes_list:
            self.nodes_attr_list.append(self.get_summary_entity_attr(entity))
        
        return
    
    #====================================================节点属性处理====================================================
    def get_summary_entity_attr(self, entity):
        '''
        将不同类型的实体的属性统一管理, 形成向量格式
        不存在的属性可以padding 0
        输入：实体节点对象
        输出：属性向量(float)
        参考：self.attr_vector_list 定义了属性向量每一维的含义
        '''
        vector = [0.] * self.attr_dim
        entity_attr_dict = entity.__dict__
        self.j = 0
        #通用的属性
        for i in range(self.attr_dim_list[0]):
            #值不为float，需要转换为float类型
            if self.attr_vector_list_all_1[i] in ['side', 'ClassName', 'strName', 'strActiveUnitStatus', 'strDamageState']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_all_1[i], entity)
            else:
                
                #值本身就为float类型，直接使用
                vector[self.j] = entity_attr_dict[self.attr_vector_list_all_1[i]]

            self.j += 1

        #通用的属性——属性值不为1维，需要先通过对应get函数来调出属性值
        for i in range(self.attr_dim_list[1]):
            vector[self.j] = self.parse_attr2(self.attr_vector_list_all_2[i], entity)
            self.j += 1
        

        #飞机专有的属性
        for i in range(self.attr_dim_list[2]):
            if self.attr_vector_list_aircrafts[i] in ['strFuelState']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_aircrafts[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_aircrafts[i]]
                except:
                    pass
            self.j += 1
    

        #TODO 以下属性的定义未完善
        #设施专有的属性
        for i in range(self.attr_dim_list[3]):
            if self.attr_vector_list_facilities[i] in ['']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_facilities[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_facilities[i]]
                except:
                    pass
            self.j += 1
        #舰船专有的属性
        for i in range(self.attr_dim_list[4]):
            if self.attr_vector_list_ships[i] in ['']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_ships[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_ships[i]]
                except:
                    pass
            self.j += 1
        #潜艇专有的属性
        for i in range(self.attr_dim_list[5]):
            if self.attr_vector_list_submarines[i] in ['']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_submarines[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_submarines[i]]
                except:
                    pass
            self.j += 1
        #武器专有的属性
        for i in range(self.attr_dim_list[6]):
            if self.attr_vector_list_weapons[i] in ['']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_weapons[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_weapons[i]]
                except:
                    pass
            self.j += 1
        #卫星专有的属性
        for i in range(self.attr_dim_list[7]):
            if self.attr_vector_list_satellites[i] in ['']:
                vector[self.j] = self.parse_attr(self.attr_vector_list_satellites[i], entity)
            else:
                try:
                    vector[self.j] = entity_attr_dict[self.attr_vector_list_satellites[i]]
                except:
                    pass
            self.j += 1


        assert(self.j==self.attr_dim)
        for i in range(len(vector)):
            if vector[i] != None:
                vector[i] = float(vector[i])
            #TODO 暂时用0.填充None
            else:
                vector[i] = 0.
        return vector
    
    def parse_attr2(self, attr_name, entity):
        '''
        将多维非数值类型的属性转换为数值类型
        解析失败自动填充0.
        '''
        #TODO 未定义
        # if attr_name == 'get_mounts()':
        #     return entity.get_mounts()
        # if attr_name == 'get_ai_targets()':
        #     return entity.get_ai_targets()
        # if attr_name == 'get_loadout()':
        #     return entity.get_loadout()
        # if attr_name == 'get_sensor()':
        #     return entity.get_sensor()
        # if attr_name == 'get_weapon_infos()':
        #     return entity.get_weapon_infos()
        return None


    def parse_attr(self, attr_name, entity):
        '''
        将非数值类型的属性转换为数值类型
        解析失败自动填充0.
        '''
        if attr_name == 'side':
            return self.parse_side_attr(attr_name, entity)
        if attr_name == 'ClassName':
            return self.parse_ClassName_attr(attr_name, entity)
        if attr_name == 'strName':
            return self.parse_strName_attr(attr_name, entity)
        if attr_name == 'strActiveUnitStatus':
            return self.parse_strActiveUnitStatus_attr(attr_name, entity)
        if attr_name == 'strDamageState':
            return self.parse_strDamageState_attr(attr_name, entity)
        if attr_name == 'strFuelState':
            return self.parse_strFuelState_attr(attr_name, entity)
        
        return None
        # return 0.
        
    def parse_side_attr(self, attr_name, entity):
        '''
        将side属性转换为数值
        解析失败自动填充0.
        '''
        #根据self.num_nodes_self判断当前实体是blue=1.0还是red=2.0
        if self.nodes_guid_list.index(entity.strGuid) < self.num_nodes_self:
            return 1.
        else:
            return 2.



    def parse_ClassName_attr(self, attr_name, entity):
        '''
        将ClassName属性转换为数值
        解析失败自动填充0.
        '''
        mapping_dict = {'CAircraft':1., 'CFacility':2., 'CShip':3., 'CSubmarine':4., 'CWeapon':5., 'CSatellite':6.}
        try:
            return mapping_dict[entity.__dict__[attr_name]]
        except:
            return None #Or 0.

    def parse_strName_attr(self, attr_name, entity):
        '''
        将name属性转换为数值
        解析失败自动填充0.
        '''
        try:
            return self.nodes_guid_list.index(entity.strGuid) + 1. 
            #TODO 由于strName是唯一的，直接用实体在列表中的编号进行表示。但是无法捕捉相同型号的单元之间的相似性
        except:
            return None #Or 0.
        # return 0.
    
    def parse_strActiveUnitStatus_attr(self, attr_name, entity):
        '''
        将strActiveUnitStatus属性转换为数值
        解析失败自动填充0.
        '''
        #TODO 调用sentence_embedding方法直接得到嵌入
        return None
    
    def parse_strDamageState_attr(self, attr_name, entity):
        '''
        将strDamageState属性转换为数值
        解析失败自动填充0.
        '''
        #TODO 调用sentence_embedding方法直接得到嵌入
        return None
    
    def parse_strFuelState_attr(self, attr_name, entity):
        '''
        将strFuelState属性转换为数值
        解析失败自动填充0.
        '''
        #TODO 调用sentence_embedding方法直接得到嵌入
        return None
    
    #====================================================边处理====================================================
    def identify_edge(self):
        '''
        根据self.nodes_list的节点信息，抽取出节点之间的关系，
        可以允许多种类型的边的存在，多种类型的边的储存方式？
        可选的边的类型参考self.admissible_edge_type
        暂定为有向边:self.edges_index_list[0]为起点，[1]为终点
        '''
        self.edges_index_list = [[],[]]
        #区分不同类型的边，索引对应着self.admissible_edge_type
        self.edges_type_list = []
        #飞机与机场的关系：m_CurrentHostUnit(facility-->aircraft)
        for entity in self.nodes_list:
            if entity.ClassName == 'CAircraft':
                aircraft_index = self.nodes_guid_list.index(entity.strGuid)
                airport_guid = entity.m_CurrentHostUnit
                if airport_guid in self.nodes_guid_list:
                    airport_index = self.nodes_guid_list.index(airport_guid)
                    self.edges_index_list[0].append(airport_index)
                    self.edges_index_list[1].append(aircraft_index)
                    self.edges_type_list.append(0)             
        #武器与发射单元的关系：m_FiringUnitGuid(unit-->weapon)
            if entity.ClassName == 'CWeapon':
                weapon_index = self.nodes_guid_list.index(entity.strGuid)
                firingUnit_guid = entity.m_FiringUnitGuid
                if firingUnit_guid in self.nodes_guid_list:
                    firingUnit_index = self.nodes_guid_list.index(firingUnit_guid)
                    self.edges_index_list[0].append(firingUnit_index)
                    self.edges_index_list[1].append(weapon_index)
                    self.edges_type_list.append(1)
        #武器与打击目标的关系：m_PrimaryTargetGuid(weapon-->target)
            if entity.ClassName == 'CWeapon':
                weapon_index = self.nodes_guid_list.index(entity.strGuid)
                target_Contact_guid = entity.m_PrimaryTargetGuid
                try:
                    target_guid = self.side_self.situation.get_obj_by_guid(target_Contact_guid).get_actual_unit().strGuid
                    if target_guid in self.nodes_guid_list:
                        target_index = self.nodes_guid_list.index(target_guid)
                        self.edges_index_list[0].append(weapon_index)
                        self.edges_index_list[1].append(target_index)
                        self.edges_type_list.append(2) 
                except:
                    # TODO 有的guid查不出对应的实体？！
                    # print(self.side_self.situation.get_obj_by_guid(target_Contact_guid), target_Contact_guid)
                    pass


        #TODO 为边设置属性
        self.edges_attr_list = None

        return
    
    #====================================================图处理====================================================
    def identify_graph(self):
        '''
        将图处理为适于图表示学习的格式
        '''
        self.identify_node()
        self.identify_edge()

        if self.args.inverse_edge_dir:
            l1 = self.edges_index_list[0].copy()
            l2 = self.edges_index_list[1].copy()
            self.edges_index_list = [l2, l1]

        if self.args.if_undir_edge:
            l1 = self.edges_index_list[0].copy()
            l2 = self.edges_index_list[1].copy()
            self.edges_index_list = [(l1+l2).copy(), (l2+l1).copy()]


        return self.nodes_attr_list, self.edges_index_list, self.edges_attr_list, self.edges_type_list