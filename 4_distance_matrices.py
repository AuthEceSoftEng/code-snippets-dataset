import os
import pandas as pd
import numpy as np
import time
import xml.etree.ElementTree as ET
from joblib import dump
from functools import partial
from scipy.spatial.distance import squareform
from properties import resultsPath
from utils.node_tree import ast_tree_to_node_tree
from utils.PyGram import Profile
from utils.parallel import pool_of_workers

def pq_gram_distance(ast_profiles, filepath, total, tree_index):

    print("File: " + filepath + " total: " + str(total) + " current: " + str(tree_index))

    vector = np.zeros(len(ast_profiles))

    for i in range(tree_index+1):
        try:
            vector[i] = int(ast_profiles[tree_index].edit_distance(ast_profiles[i]) * 1000)
        except:
            vector[i] = 1000

    return vector


def pq_grams_profiles(ast_trees):

    """
    for the pq-gram algorithm, compute the Profile of each ast tree
    """

    # profiles = [Profile(ast_tree) for ast_tree in ast_trees]

    profiles = []

    for ast_tree in ast_trees:
        try:
            profiles.append(Profile(ast_tree_to_node_tree(ET.fromstring(ast_tree))))
        except:
            profiles.append([])

    return profiles

def compute_distance_matrix(ast_trees, filepath, total):
    """
    Calculate the distance matrix of the data in parallel

    :param ast_trees:
    :return: the distance matrix
    """

    samples = len(ast_trees)

    ast_trees_index = range(samples)

    profiles = pq_grams_profiles(ast_trees)
    func = partial(pq_gram_distance, profiles, filepath, total)

    # We make use of multiprocessing library in order to compute the distance matrix in parallel
    # Each worker call the ast_tree_distances function and creates a csv file with the blocks
    # of a repository
    t1 = time.time()
    outputs = pool_of_workers(4, func, ast_trees_index)
    t2 = time.time()

    elapsed_time = t2 - t1

    print("distance matrix computation time: " + str(elapsed_time))

    matrix = np.array(outputs, dtype='int')

    return matrix

if __name__ == '__main__':
    for ind, file in enumerate(os.listdir(resultsPath)):
        if ((not file.endswith(".csv")) or (not file.startswith("df"))): continue
        cc = file.split("_")[1]
        nn1 = file.split("_")[2]
        nn2 = file.split("_")[3].split(".csv")[0]
        filepath = os.path.join(resultsPath, "distance_matrix_" + cc + "_" + nn1 + "_" + nn2 + ".joblib")
        if (os.path.exists(filepath)): continue

        print(str(ind + 1) + "/" + str(len(os.listdir(os.path.join(resultsPath, "test")))))
        df = pd.read_csv(os.path.join(resultsPath, file))

        print(len(df.index))

        distance_matrix = compute_distance_matrix(df["ast_code"], filepath, len(df.index))
        distance_matrix = distance_matrix + distance_matrix.T
        distance_matrix = squareform(distance_matrix, checks=False)
        dump(distance_matrix, filepath)