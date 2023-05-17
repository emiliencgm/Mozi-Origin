import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Graph_Representation_MOZI")
    parser.add_argument("--output_dim", type=int, default=10, help='output dimension of GCN encoder')
    parser.add_argument("--temp_tau", type=float, default=0.1, help='temperature hyperparameter tau in InfoNCE loss')
    parser.add_argument("--p_drop_edge", type=float, default=0.1, help='probability for dropping an edge in augmentation')
    parser.add_argument("--p_mask_attr", type=float, default=0.1, help='probability for masking an attribute in augmentation')
    parser.add_argument("--num_epochs_GCL", type=int, default=100, help='number of epochs for training encoder in each step of MOZI')
    parser.add_argument("--visual_step", type=int, default=10, help='visualize the graph every visual_step in MOZI stepping')
    parser.add_argument("--if_tsne", type=int, default=0, help='whether use t_SNE in visualization')
    parser.add_argument("--if_nx", type=int, default=1, help='whether use networkx in visualization')
    parser.add_argument("--inverse_edge_dir", type=int, default=0, help='whether inverse edges direction')
    parser.add_argument("--if_undir_edge", type=int, default=0, help='whether transfer the graph to undirected one(by copying the edge_index)')
    parser.add_argument("--view_mode", type=str, default='origin_augment', help='origin_view vs augmented_view or augmented_view1 vs augmented_view2')
    parser.add_argument("--if_cuda", type=int, default=1, help='whether use cuda to train the GNN')
    parser.add_argument("--if_show_edge_name", type=int, default=0, help='whether show edge name in visualization')
    parser.add_argument("--if_load_encoder", type=int, default=0, help='whether load the GNN encoder rather than training from scratch')
    parser.add_argument("--augment_mode", type=str, default='attr_mask', help='augmentation method: edge_drop, attr_mask')


    return parser.parse_args()