# readability-dataset
Dataset builder for Readability Dataset

## Prerequisites
1. Make sure that you have Java installed (suggested version jdk-11.0.2)
2. Download and extract the SourceMeter tool from [this website](https://sourcemeter.com/download)
3. Download and extract the Readability tool from [this website](https://dibt.unimol.it/report/readability/) (direct link available [here](https://dibt.unimol.it/report/readability/files/readability.zip))
4. Download and extract the CodeSearchNet Java corpus snippets from [this repo](https://github.com/github/CodeSearchNet#data-details) (direct link available [here](https://s3.amazonaws.com/code-search-net/CodeSearchNet/v2/java.zip))
5. Edit file `properties.py` to set the path of Java, the path to SourceMeterJava.exe and rsm.jar, the path to the dataset, the path of the results folder, and a directory to be used as temporary directory.

## Building the dataset
Execute the script `1_run_all_metrics.py` and the results folder will be populated with the metrics in CSV format.
