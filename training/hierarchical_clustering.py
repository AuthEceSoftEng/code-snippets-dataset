from sklearn.cluster import AgglomerativeClustering

def ag_hierarchical(affinity, linkage_criterion, num_clusters, data):

    """
    Agglomerative Hierarchical Clustering

    :param affinity: distance metric used for linkage
    :param num_clusters
    :param data: instances to cluster or distance matrix if affinity is precomputed
    :param linkage_criterion
    :return: clustering results
    """

    model = AgglomerativeClustering(affinity=affinity, linkage=linkage_criterion, n_clusters=num_clusters)

    clustering = model.fit(data)

    return clustering
