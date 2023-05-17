# 时间 ： 2023/5/10 08:55
# 作者 ： CGM
# 文件 ： garph_main.py
# 项目 ： mozi_graph_representation
# 版权 ： 我自己的

from graph_representation.graph_construct import Graph_Construct
from graph_representation.graph_learning import Graph_Learning
from graph_representation.graph_visualization import Graph_Visualization
from graph_representation.graph_parse import parse_args
from pprint import pprint

class Graph:
    '''
    图表示的接口类
    '''
    def __init__(self, side_self, side_ops):
        self.side_self = side_self
        self.side_ops = side_ops
        self.args = parse_args()
        pprint(self.args)
        self.Construct = Graph_Construct(side_self=side_self, args=self.args, side_ops=side_ops)
        self.Visual = Graph_Visualization(self.Construct, args=self.args)
        self.Learning = Graph_Learning(self.Construct, self.Visual, self.args)

    def graph_representation_blue(self):
        self.Learning.train()
