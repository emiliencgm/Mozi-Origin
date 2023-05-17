import torch
import numpy as np
import torch.nn.functional as F
from torch_geometric.data import Data


class GCL(torch.nn.Module):
    '''
    图对比学习框架
    '''
    def __init__(self, args):
        self.args = args
        #InfoNCE的temperature超参数
        self.tau = args.temp_tau
        #随机丢弃边的概率
        self.p_drop_edge = args.p_drop_edge
        self.p_mask_attr = args.p_mask_attr

    def edge_drop(self, edge_index, nodes_attr, edge_weight):
        '''
        数据增强——random edge drop
        '''
        num_edges = len(edge_index[0])
        keep_idx = self.randint_choice(num_edges, size=int(num_edges * (1 - self.p_drop_edge)), replace=False)
        edge_source = np.array(edge_index[0].copy())
        edge_target = np.array(edge_index[1].copy())
        edge_source = list(edge_source[keep_idx])
        edge_target = list(edge_target[keep_idx])

        edge_index_augment = [edge_source, edge_target]

        _edge_index = torch.tensor(edge_index_augment, dtype=torch.long)
        x = torch.tensor(nodes_attr, dtype=torch.float)
        data_augment = Data(x=x, edge_index=_edge_index.contiguous(), edge_attr=edge_weight)

        return data_augment
    
    def attr_mask(self, edge_index, nodes_attr, edge_weight):
        '''
        数据增强——random attribute mask（不是删掉该维度，而是变成0）
        '''
        num_attrs = len(nodes_attr[0])
        keep_idx = self.randint_choice(num_attrs, size=int(num_attrs * (1 - self.p_mask_attr)), replace=False)
        nodes_attr_augment = []
        for node_attr in nodes_attr:
            node_attr_augment = node_attr.copy()
            for i in range(len(node_attr_augment)):
                if i not in keep_idx:
                    node_attr_augment[i] = 0.
            nodes_attr_augment.append(node_attr_augment)

        _edge_index = torch.tensor(edge_index, dtype=torch.long)
        x = torch.tensor(nodes_attr_augment, dtype=torch.float)
        data_augment = Data(x=x, edge_index=_edge_index.contiguous(), edge_attr=edge_weight)

        return data_augment
    
    def randint_choice(self, high, size=None, replace=False, p=None, exclusion=None):
        """
        Return random integers from `0` (inclusive) to `high` (exclusive).
        """
        a = np.arange(high)
        if exclusion is not None:
            if p is None:
                p = np.ones_like(a)
            else:
                p = np.array(p, copy=True)
            p = p.flatten()
            p[exclusion] = 0
        if p is not None:
            p = p / np.sum(p)
        sample = np.random.choice(a, size=size, replace=replace, p=p)
        return sample

    def contrastive_loss(self, embs_1, embs_2):
        '''
        InfoNCE loss
        BC loss实现
        '''
        embs_1 = F.normalize(embs_1, dim = -1)
        embs_2 = F.normalize(embs_2, dim = -1)

        ratings = torch.matmul(embs_1, torch.transpose(embs_2, 0, 1))
        ratings_diag = torch.diag(ratings)

        numerator = torch.exp(ratings_diag / self.tau)
        denominator = torch.sum(torch.exp(ratings / self.tau), dim = 1)
        loss = torch.mean(torch.negative(torch.log(numerator/denominator)))
        return loss

