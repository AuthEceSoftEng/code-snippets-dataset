import os
import pandas as pd
from joblib import load
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_samples
from statistics import mean
import matplotlib.pyplot as plt
import numpy
from collections import Counter
from training.clustering_tools import clusters_selection
from training.hierarchical_clustering import ag_hierarchical
from properties import resultsPath

def clustering_analysis(filename, min_clusters = 10, max_clusters = 50000, size_threshold = 100):
    """
    Complete clustering analysis using silhouette coefficient to determine the optimum number of clusters
    and make a selection of the best clusters based on a number of parameters

    :param filename:
    :param min_clusters:
    :param max_clusters:
    :param step:
    :param size_threshold:
    :return:
    """
    distance_matrix = load(os.path.join(resultsPath, filename))

    distance_matrix = squareform(distance_matrix)

    step = int(numpy.floor((numpy.min([max_clusters, len(distance_matrix)]) - min_clusters) / 50))

    x = range(min_clusters, numpy.min([max_clusters, len(distance_matrix)]), step)

    max_silhouette_coefficient = -1

    silhouette_average_scores = []

    optimum_n_clusters = 0

    for n_clusters in x:

        print(n_clusters)

        clustering = ag_hierarchical('precomputed', 'average', n_clusters, distance_matrix)

        clusters = clustering.labels_

        sil_sampl = silhouette_samples(distance_matrix, clusters, metric='precomputed')

        average_silh = mean(sil_sampl)

        silhouette_average_scores.append(average_silh)

        if average_silh > max_silhouette_coefficient:
            max_silhouette_coefficient = average_silh
            optimum_n_clusters = n_clusters

    ax1 = plt.axes()

    ax1.axhline(y=max_silhouette_coefficient, color="red", linestyle="--")

    plt.plot(x, silhouette_average_scores, 'bo-')
    plt.xlabel("Number Of Clusters", fontsize=12)
    plt.ylabel("Average Silhouette Score", fontsize=12)

    # plt.show()

    print("optimum number of clusters:" + str(optimum_n_clusters))

    print("max silhouette coefficient:" + str(max_silhouette_coefficient))

    clustering = ag_hierarchical('precomputed', 'average', optimum_n_clusters, distance_matrix)

    clusters = clustering.labels_

    points_per_cluster = Counter(clusters)

    selected_clusters = clusters_selection(points_per_cluster, size_threshold)
    
    return clusters, selected_clusters

if __name__ == '__main__':
    clustersDF = pd.DataFrame({"url": [], "code": [], "cluster": []})
    joblibFiles = [f for f in os.listdir(resultsPath) if f.endswith(".joblib")]
    for ind, file in enumerate(joblibFiles):
        cc = file.split("_")[2]
        nn1 = file.split("_")[3]
        nn2 = file.split("_")[4].split(".joblib")[0]
        filepath = os.path.join(resultsPath, "df_" + cc + "_" + nn1 + "_" + nn2 + ".csv")

        print(str(ind + 1) + "/" + str(len(joblibFiles)))
        df = pd.read_csv(os.path.join(resultsPath, filepath))
        df_new = df.loc[:, ["url", "code"]]
        df_new["cluster"] = "-"

        clusters, selected_clusters = clustering_analysis(file)
        for index, row in df_new.iterrows():
            if (clusters[index] in selected_clusters):
                df_new.loc[index, "cluster"] = clusters[index]
        
        clustersDF = pd.concat([clustersDF, df_new], ignore_index=True)

    clustersDF.to_csv(os.path.join(resultsPath, "clusters", "clusters.csv"))
    print(len(clustersDF.index))
