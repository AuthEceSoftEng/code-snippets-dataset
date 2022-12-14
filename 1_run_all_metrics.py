import os
import json
import time
import codecs
import requests
from collections import defaultdict
from libs.sourcemeter import MetricsAnalyzer
from libs.readability import ReadabilityAnalyzer
from properties import datasetPath, resultsPath, javaExePath, rsmJarPath, sourcemeterExePath, tempDirPath

ra = ReadabilityAnalyzer(javaExePath, rsmJarPath, tempDirPath)
ma = MetricsAnalyzer(javaExePath, sourcemeterExePath, tempDirPath)

# Read all metrics and violations
analysismetrics = []
with open("libs/metrics.csv") as infile:
	for line in infile:
		analysismetrics.append(line.split(';')[0])
violations = []
with open("libs/violations.csv") as infile:
	for line in infile:
		violations.append(line.split(';')[0])
readabilitymetrics = []
with open("libs/readabilitymetrics.json") as infile:
	rmetrics = json.load(infile)
	for metriccategory in rmetrics:
		for metric in rmetrics[metriccategory]:
			readabilitymetrics.append(metriccategory + "_" + metric)

if not os.path.exists(resultsPath):
	os.makedirs(resultsPath)

# Iterate over all snippets in dataset
for directory in ["train", "valid", "test"]:
	for jsonlfile in os.listdir(os.path.join(datasetPath, directory)):
		snippetsPath = os.path.join(datasetPath, directory, jsonlfile)
		if not os.path.exists(os.path.join(resultsPath, jsonlfile.split(".")[0] + ".csv")):
			with open(os.path.join(resultsPath, jsonlfile.split(".")[0] + ".csv"), 'w') as outfile:
				outfile.write("url;" + ";".join(analysismetrics) + ";" + ";".join(violations) + ";" + ";".join(readabilitymetrics) + "\n")
				with codecs.open(snippetsPath, encoding='utf-8', errors='ignore') as infile:
					for i, line in enumerate(infile):
						snippetjson = json.loads(line.strip())

						# format code and docstring
						code = snippetjson["original_string"]
						for codeline in reversed(code.split('\n')):
							if '}' in codeline:
								spaces = codeline.split('}')[0]
								break
						docstring = snippetjson["docstring"]
						if docstring:
							documentation = spaces + "/**\n"
							for docline in docstring.split("\n"):
								if "/*" not in docline:
									documentation += spaces + " * " + docline + "\n"
							documentation += spaces + " */\n"
						code = spaces + snippetjson["original_string"]
						#print(documentation + code)

						try:
							# Run static analysis
							maresults = ma.analyze_method(documentation + code)
							analysisresults = []
							for metric in analysismetrics:
								analysisresults.append(maresults["metrics"][metric])
							violationresults = []
							for violation in violations:
								if violation in maresults["violations"]["stats"]:
									violationresults.append(maresults["violations"]["stats"][violation])
								elif violation in maresults["violations"]["violations"]:
									if type(maresults["violations"]["violations"][violation]) is list:
										violationresults.append(len(maresults["violations"]["violations"][violation]))
									else:
										violationresults.append(1)
								else:
									violationresults.append(0)

							# Run readability analysis
							reresults = ra.analyze_method(documentation + code)
							readabilityresults = []
							for metric in readabilitymetrics:
								metric_category = metric.split("_")[0]
								metric = metric[len(metric.split("_")[0]) + 1:]
								if metric_category in reresults and metric in reresults[metric_category]:
									readabilityresults.append(reresults[metric_category][metric])

							analysisresults = [str(s) for s in analysisresults]
							violationresults = [str(s) for s in violationresults]
							readabilityresults = [str(s) for s in readabilityresults]
						except:
							# Use -1 as error code
							analysisresults = [str(-1) for s in analysismetrics]
							violationresults = [str(-1) for s in violations]
							readabilityresults = [str(-1) for s in readabilitymetrics]

						# Write results to file
						try:
							outfile.write(snippetjson["url"] + ";" + ";".join(analysisresults) + ";" + ";".join(violationresults) + ";" + ";".join(readabilityresults) + "\n")
							outfile.flush()
						except UnicodeEncodeError: # this exception used only to catch unicode errors in filenames (very rare case)
							pass

						# Delete temporary files
						if i % 10 == 0:
							ra.cleanup()
							ma.cleanup()

# Delete any leftover temporary files
ra.cleanup()
ma.cleanup()

