import numpy as np
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


def compute_centroids(clusters, distance_matrix):
    """
    Compute the centroid for each cluster, choose as centroid the point with the smallest average distance
    from the other points of the cluster
    """

    n_clusters = max(clusters) + 1

    centroids = np.zeros(n_clusters)

    for cluster in range(n_clusters):

        # find the points and the size of each cluster
        cluster_points = np.where(clusters == cluster)[0]
        n_points = len(cluster_points)

        # initialization of the minimum sse (using a large value) and the centroid of te cluster (using the first point)
        min_sse = 1000000
        centroids[cluster] = cluster_points[0]

        for point in cluster_points:

            # average distance
            sse = sum(distance_matrix[point, cluster_points]) / n_points

            if sse < min_sse:

                min_sse = sse
                centroids[cluster] = point

    return centroids

