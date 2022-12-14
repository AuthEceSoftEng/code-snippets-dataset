import io	
import os
import json
import subprocess
from subprocess import PIPE, STDOUT
from properties import javaExePath, rsmJarPath, tempDirPath

class ReadabilityAnalyzer(object):
	"""
	Class used as a python binding to the RSM readability tool by Scalabrino et al. It contains functions for
	parsing java code and extracting readability metrics from java projects, classes and methods.
	"""
	def __init__(self, path_to_Java_exe, path_to_RSM_jar, path_to_RSM_temp_dir):
		"""
		Initializes this extractor.
		
		:param path_to_Java_exe: the path to the Java executable.
		:param path_to_RSM_jar: the path to the rsm.jar executable java archive.
		:param path_to_RSM_temp_dir: the path to the RSM temp directory for files/results.
		"""
		self.path_to_Java_exe = path_to_Java_exe
		self.path_to_RSM_jar = path_to_RSM_jar
		self.path_to_RSM_temp_dir = path_to_RSM_temp_dir
		if not os.path.exists(self.path_to_RSM_temp_dir):
			os.makedirs(self.path_to_RSM_temp_dir)

	def run_analysis(self, filepath, include_metrics = False, normalize_metrics = True):
		cmd = [self.path_to_Java_exe, "-cp", self.path_to_RSM_jar, "it.unimol.readability.metric.runnable.ExtractMetrics", filepath]
		proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.dirname(self.path_to_RSM_jar))
		if include_metrics:
			metrics = {"Scalabrino": {}, "BW": {}, "Posnett": {}, "Dorn": {}}
		results = {"Scalabrino": {}, "BW": {}, "Posnett": {}, "Dorn": {}}
		for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
			line = line.strip()

			# Split and handle result
			if ":" in line:
				metric, result = line.split(":")[0], line.split(":")[1]
				try: result = float(result)
				except: result = None

			if line.startswith("New"):
				# Handle Scalabrino metrics
				metric = metric[4:]
				metric_category = "Scalabrino"
				# Get metric name and metric type
				if metric.endswith("MIN"): metric_name, metric_type = metric[:-4], "minimum"
				elif metric.endswith("MAX"): metric_name, metric_type = metric[:-4], "maximum"
				elif metric.endswith("AVG"): metric_name, metric_type = metric[:-4], "average"
				elif metric.endswith("Standard"): metric_name, metric_type = metric[:-9], "standard"
				elif metric.endswith("Normalized"): metric_name, metric_type = metric[:-11], "normalized"
				else: metric_name, metric_type = metric, None

			elif line.startswith("BW"):
				# Handle BW metrics
				metric = metric[3:]
				metric_category = "BW"
				# Get metric name and metric type
				if metric.startswith("Avg"): metric_name, metric_type = metric[4:], "average"
				elif metric.startswith("Max"): metric_name, metric_type = metric[4:], "maximum"
				if metric_name == "indentation length": metric_name = "indentation" # minor correction to keep the same names for metrics

			elif line.startswith("Posnett"):
				# Handle Posnett metrics
				metric = metric[8:]
				metric_category = "Posnett"
				# Get metric name and metric type
				if metric.startswith("Visual X"): metric_name, metric_type = metric[9:], "x"
				elif metric.startswith("Visual Y"): metric_name, metric_type = metric[9:], "y"
				else: metric_name, metric_type = metric, None

			elif line.startswith("Dorn"):
				# Handle Dorn metrics
				metric = metric[5:]
				metric_category = "Dorn"
				# Get metric name and metric type
				if metric.startswith("Visual X"): metric_name, metric_type = metric[9:], "x"
				elif metric.startswith("Visual Y"): metric_name, metric_type = metric[9:], "y"
				else: metric_name, metric_type = metric, None

			else:
				continue

			# Create id for metric
			metric_id = "".join(m if m.isalnum() else "_" for m in metric_name.lower())

			if normalize_metrics and metric_type:
				metric_id += "_" + metric_type
				metric_name += " " + metric_type[0].upper()
				if len(metric_type) > 1: metric_name += metric_type[1:]

			if metric_type and metric_id not in results[metric_category]: results[metric_category][metric_id] = {}

			# Add metric to metrics and result to results
			if include_metrics:
				metrics[metric_category][metric_id] = metric_name
			if metric_type and not normalize_metrics: results[metric_category][metric_id][metric_type] = result
			else: results[metric_category][metric_id] = result

		# Read also Scalabrino readability
		with open(filepath) as infile:
			filedata = infile.read()
		with open(filepath, 'w') as outfile:
			outfile.write("class MyClass{\n\n" + filedata + "\n}\n")
		cmd = [self.path_to_Java_exe, "-jar", self.path_to_RSM_jar, filepath]
		proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.dirname(self.path_to_RSM_jar))
		for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
			line = line.strip()
			line = line.split("\t")
			if len(line) > 1:
				try:
					result = float(line[1])
					if include_metrics:
						metrics["Scalabrino"]["readability"] = "Readability"
					results["Scalabrino"]["readability"] = result
				except:
					if include_metrics:
						metrics["Scalabrino"]["readability"] = "Readability"
					results["Scalabrino"]["readability"] = None

		if include_metrics:
			return metrics, results
		else:
			return results

	def analyze_method(self, method_code):
		filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
		with open(filename, 'w') as outfile:
			# outfile.write("class MyClass{\n\n")
			outfile.write(method_code + "\n")
			# outfile.write("}\n")
		return self.run_analysis(filename)

	def cleanup(self):
		filename = os.path.join(self.path_to_RSM_temp_dir, "temp.java")
		try:
			os.remove(filename)
		except OSError:
			pass

if __name__ == '__main__':
	ra = ReadabilityAnalyzer(javaExePath, rsmJarPath, tempDirPath)

	results = ra.analyze_method(r"""	private CSVSettings parseCsvSettings(JSONObject headRecord) throws Exception {
		JSONObject csv = headRecord.getJSONObject("_csv");
		
		CSVSettings csvSettings = new CSVSettings();
		
		JSONArray columnArr = csv.getJSONArray("columns");
		for(int i=0,e=columnArr.length(); i<e; ++i){
			Object columnObj = columnArr.get(i);
			if( columnObj instanceof JSONObject ){
				JSONObject jsonColumnDef = (JSONObject)columnObj;
				String name = jsonColumnDef.optString("name",null);
				String label = jsonColumnDef.optString("label",null);
				
				if( null == name ){
					throw new Exception("Column definition must have a name");
				}
				if( null == label ){
					label = name;
				}
				
				CSVColumn csvColumn = new CSVColumn();
				csvColumn.setName(name);
				csvColumn.setLabel(label);
				
				csvSettings.addColumn(csvColumn);
				
			} else {
				throw new Exception("_csv.columns must be array of column definitions (objects)");
			}
		}
		
		return csvSettings;
	}""")
	
	print(json.dumps(results, indent=3))

	ra.cleanup()
