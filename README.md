# readability-dataset
Dataset builder for Readability Dataset

## Prerequisites
1. Make sure that you have Java installed (suggested version jdk-11.0.2)
2. Download and extract the SourceMeter tool from [this website](https://sourcemeter.com/download)
3. Download and extract the Readability tool from [this website](https://dibt.unimol.it/report/readability/) (direct link available [here](https://dibt.unimol.it/report/readability/files/readability.zip))
4. Download and extract the CodeSearchNet Java corpus snippets from [this repo](https://github.com/github/CodeSearchNet#data-details) (direct link available [here](https://s3.amazonaws.com/code-search-net/CodeSearchNet/v2/java.zip))
5. Edit file `properties.py` to set the path of Java, the path to SourceMeterJava.exe and rsm.jar, the path to the dataset, the path of the results folder, and a directory to be used as temporary directory.

## Building the dataset
1. Execute the script `1_run_all_metrics.py` and the results folder will be populated with the metrics in CSV format.
2. Execute the script `2_run_asts.py` in order to create the files that contain the AST representations within the results folder.
3. Execute the script `3_preclustering.py` to split the code snippets into smaller groups, with respect to their cyclomatic complexity and number of operators.
4. Execute the script `4_distance_matrices.py`, which calculates the distance matrices between the snippets of each file and stores the results.
5. Execute the script `5_clustering.py` in order to make use of the generate distance matrices and perform the hierarchical clustering.

## Migrating to MongoDB
1. Create the file `mongo/.env` based on the file `mongo/.env.sample` to set the MongoDB uri and the path to the results folder, the path to the dataset, the path to the ASTs folder and the path to the generated clusters folder.
2. Execute the nodejs script `mongo/upload-metrics.js` in order to parse all the generated files of the analysis and migrate the results to a MongoDB instance.
