# 时间 ： 2023/5/10 08:55
# 作者 ： CGM
# 文件 ： garph_main.py
# 项目 ： mozi_graph_representation
# 版权 ： 我自己的

'''
图表示学习部分
采用自监督图对比框架
输入：图邻接矩阵, 节点属性 (, 边的属性/id)
输出：节点embedding
GNN编码器：GCN
'''
import torch
from torch_geometric.data import Data
from tqdm import tqdm
import copy
from graph_representation.graph_learning_GNN import GCN
from graph_representation.graph_learning_GCL import GCL


class Graph_Learning:
    '''
    可以设计为：整个推演只有一个encoder，每轮的图都作为一个训练数据    
    '''
    def __init__(self, graph_construct, graph_visual, args):
        self.graph_construct = graph_construct
        self.graph_visual = graph_visual
        self.args = args
        self.input_dim = self.graph_construct.attr_dim
        self.output_dim = self.args.output_dim
        self.encoder_weight_file = f"graph_representation/encoder_GNN_weights.pth.tar"
        if self.args.if_load_encoder:
            try:
                self.encoder = GCN(self.input_dim, self.output_dim)
                self.encoder.load_state_dict(torch.load(self.encoder_weight_file, map_location=torch.device('cpu')))
            except:
                self.encoder = GCN(self.input_dim, self.output_dim)
        else:
            self.encoder = GCN(self.input_dim, self.output_dim)
        self.gcl = GCL(self.args)
        self.count = 0
        if self.args.if_cuda:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device('cpu')

    def train(self):
        '''
        每步推演进行一次训练，将当前态势图作为一组训练数据
        '''
        self.count += 1
        node_attr, edge_index, edge_weight, edge_type = self.graph_construct.identify_graph()
        self.node_attr = node_attr
        self.edge_index = copy.deepcopy(edge_index) #TODO 浅拷贝无法作用于二维数组
        self.edge_weight = edge_weight
        #TODO 转换为PyG数据格式，有向边， 并添加了self-loop
        for i in range(len(self.graph_construct.nodes_list)):
            self.edge_index[0].append(i)
            self.edge_index[1].append(i)
        _edge_index = torch.tensor(self.edge_index, dtype=torch.long)
        x = torch.tensor(self.node_attr, dtype=torch.float)
        self.data_origin = Data(x=x, edge_index=_edge_index.contiguous(), edge_attr=self.edge_weight)

        device = self.device
        data = self.data_origin.to(device)
        if self.args.augment_mode == 'edge_drop':
            data_augment_1 = self.gcl.edge_drop(self.edge_index, self.node_attr, self.edge_weight).to(device)
            data_augment_2 = self.gcl.edge_drop(self.edge_index, self.node_attr, self.edge_weight).to(device)
        elif self.args.augment_mode == 'attr_mask':
            data_augment_1 = self.gcl.attr_mask(self.edge_index, self.node_attr, self.edge_weight).to(device)
            data_augment_2 = self.gcl.attr_mask(self.edge_index, self.node_attr, self.edge_weight).to(device)

        optimizer = torch.optim.Adam(self.encoder.parameters(), lr=0.01, weight_decay=5e-4)

        self.encoder.train()
        for epoch in tqdm(range(self.args.num_epochs_GCL), desc='training'):
            optimizer.zero_grad()
            if self.args.view_mode == 'origin_augment':
                out_1 = self.encoder(data)
                out_2 = self.encoder(data_augment_1)
            elif self.args.view_mode == 'augment_augment':
                out_1 = self.encoder(data_augment_1)
                out_2 = self.encoder(data_augment_2)
            loss = self.gcl.contrastive_loss(out_1, out_2)
            loss.backward()
            optimizer.step()
        #保存encoder GNN模型参数
        torch.save(self.encoder.state_dict(), self.encoder_weight_file)
        #可视化
        if self.count % self.args.visual_step == 0:
            num_self = self.graph_construct.num_nodes_self
            self_color = self.graph_construct.side_self.strSideColorKey
            self.graph_visual.t_SNE(torch.tensor(self.node_attr), num_self, self_color, 'ego')
            self.graph_visual.t_SNE(self.encoder(data), num_self, self_color, 'emb')#.clone().detach()
            self.graph_visual.show_encoder(self.encoder)
            self.graph_visual.count += 1




