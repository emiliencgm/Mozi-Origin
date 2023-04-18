


from cProfile import label
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
# from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler



def get_airs_centers(X):


    X_normalize = StandardScaler().fit_transform(X)


    db = DBSCAN(eps=0.3, min_samples=10).fit(X_normalize)
    # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    # 每个数据得分类
    labels = db.labels_
    # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    centers = {}
    for i in range(len(labels)):

        if labels[i] == -1:
            continue

        if labels[i] not in centers:
            centers[labels[i]] = [X[i]]
        else:
            centers[labels[i]].append(X[i])
    max = 0
    high_threat_areas = []
    for v in centers.values():
        if len(v) > max :
            max = len(v)
            high_threat_areas = v

    return np.mean(high_threat_areas,axis=0),len(high_threat_areas)



