import csv
import sys

csv.field_size_limit(sys.maxsize)

def clusters_selection(points_per_cluster, size_threshold):
    """
    After clustering process we choose only the clusters with size bigger than size_threshold

    :param centroids:
    :param clusters:
    :param data:
    :param points_per_cluster:
    :param size_threshold
    :param cohesion_threshold:
    :param repos_threshold:
    :return: the selected clusters
    """

    n_clusters = max(points_per_cluster, key=int)

    selected_clusters = []

    for cluster in range(n_clusters):

        if points_per_cluster[cluster] >= size_threshold:
            selected_clusters.append(cluster)

    return selected_clusters
