# 时间 ： 2023/5/10 08:55
# 作者 ： CGM
# 文件 ： garph_main.py
# 项目 ： mozi_graph_representation
# 版权 ： 我自己的
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import os
import torch
import networkx as nx
from tensorboardX import SummaryWriter
import time
from os.path import join


class Graph_Visualization:
    def __init__(self, graph_construct, args):
        self.count = 0
        self.graph_construct = graph_construct
        self.args = args
        if not os.path.exists('graph_representation/imgs/tsne'):
            os.makedirs('graph_representation/imgs/tsne', exist_ok=True)
        if not os.path.exists('graph_representation/imgs/nx'):
            os.makedirs('graph_representation/imgs/nx', exist_ok=True)
        if not os.path.exists('graph_representation/runs'):
            os.makedirs('graph_representation/runs', exist_ok=True)

    def t_SNE(self, embs, num_self, self_color, filename):
        with torch.no_grad():
            #TODO perplexity
            X = TSNE(perplexity=10, init='pca', method='barnes_hut').fit_transform(embs)
            plt.rcParams['font.sans-serif'] = ['Simhei']  #显示中文
            plt.rcParams['axes.unicode_minus'] = False    #显示负号
            figsize=(15,15)
            plt.figure(figsize=figsize)
            if self_color == '蓝色':
                classes_item = ['Blue', 'Red']
                scatter_blue = plt.scatter(X[:num_self,0],X[:num_self,1], c='b', label=classes_item[0])
                scatter_red = plt.scatter(X[num_self:,0],X[num_self:,1], c='r', label=classes_item[1])
            elif self_color == '红色':
                classes_item = ['Red', 'Blue']
                scatter_red = plt.scatter(X[:num_self,0],X[:num_self,1], c='r', label=classes_item[0])
                scatter_blue = plt.scatter(X[num_self:,0],X[num_self:,1], c='b', label=classes_item[1])
            else:
                raise ValueError
            for i in range(len(self.graph_construct.nodes_list)):
                plt.text(X[i, 0], X[i, 1], self.graph_construct.nodes_list[i].strName)
            # legend_item = plt.legend(handles=scatter_item.legend_elements()[0], labels=classes_item, loc='upper left')
            # plt.gca().add_artist(legend_item)

            #是否单独绘制tSNE图像
            if self.args.if_tsne:
                plt.title(str(self.count)+'--'+filename, fontdict={'weight':'normal','size': 20})
                plt.savefig('graph_representation/imgs/tsne/'+str(self.count)+filename+'.jpg')
                #plt.show()
                plt.close()

            self.nx_graph(X, filename, num_self, self_color)
    
    def nx_graph(self, X, filename, num_self, self_color):
        with torch.no_grad():
            G = nx.DiGraph()
            # 添加对应的边和点
            for i in range(len(self.graph_construct.nodes_list)):
                G.add_node(i, desc=self.graph_construct.nodes_list[i].strName)  # 结点名称不能为str,desc为标签即结点名称
            
            for i in range(len(self.graph_construct.edges_index_list[0])):
                if self.args.if_show_edge_name:
                    type = self.graph_construct.edge_type[self.graph_construct.edges_type_list[i]]
                else:
                    type = ''
                G.add_edge(self.graph_construct.edges_index_list[0][i], self.graph_construct.edges_index_list[1][i], name=str(type))
            
            figsize=(20,20)
            plt.figure(figsize=figsize)
            plt.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, hspace=0.1, wspace=0.1)
            unobserved_red = self.graph_construct.unobserved_ops_list
            if self_color == '蓝色':
                colors = ['b']*num_self
                for node_ops in self.graph_construct.nodes_list_ops:
                    if node_ops in unobserved_red:
                        colors += 'y' #不可观测的红方以黄色显示
                    else:
                        colors += 'r'
            elif self_color == '红色':
                colors = ['r']*num_self
                for node_ops in self.graph_construct.nodes_list_ops:
                    if node_ops in unobserved_red:
                        colors += 'y' #不可观测的蓝方以黄色显示
                    else:
                        colors += 'b'
            else:
                raise ValueError
            nx.draw_networkx(G, X, with_labels=None, node_color=colors, alpha=0.8)
            # 画出标签
            node_labels = nx.get_node_attributes(G, 'desc')
            nx.draw_networkx_labels(G, X, labels=node_labels)
            # 画出边权值
            edge_labels = nx.get_edge_attributes(G, 'name')
            nx.draw_networkx_edge_labels(G, X, edge_labels=edge_labels)

            if self.args.if_nx:
                plt.title(str(self.count)+'--'+filename+f' {self_color}视角', fontdict={'weight':'normal','size': 20})
                # plt.show()
                plt.savefig('graph_representation/imgs/nx/'+str(self.count)+filename+'-nx.jpg')
                plt.close()
            plt.close()

    def show_encoder(self, model):
        '''
        可视化GNN编码器的架构和权重
        '''
        # w = SummaryWriter(join('graph_representation/runs', str(self.count)))
        w = SummaryWriter('graph_representation/runs')
        # w.add_graph(model)#GNN架构可视化
        with torch.no_grad():
            for name, param in model.named_parameters():
                try:
                    weight = param.view(-1, param.size()[0], param.size()[1])
                except:
                    weight = param.view(-1, param.size()[0], 1)
                w.add_image(name, weight, global_step=self.count)
