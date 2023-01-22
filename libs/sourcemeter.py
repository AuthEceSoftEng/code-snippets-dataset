import io	
import os
import json
import shutil
import subprocess
from subprocess import PIPE, STDOUT

class MetricsAnalyzer(object):
	"""
	Class used as a python binding to the SourceMeterJava tool. It contains functions for parsing java code
	and extracting metrics from java projects, classes and methods.
	"""
	def __init__(self, path_to_Java_exe, path_to_SourceMeterJava_exe, path_to_SourceMeterJava_temp_dir):
		"""
		Initializes this extractor.
		
		:param path_to_Java_exe: the path to the Java executable.
		:param path_to_SourceMeterJava_exe: the path to the SourceMeterJava exe.
		:param path_to_SourceMeterJava_temp_dir: the path to the SourceMeterJava temp directory for files/results.
		"""
		self.path_to_Java_exe = path_to_Java_exe
		self.path_to_SourceMeterJava_exe = path_to_SourceMeterJava_exe
		self.path_to_SourceMeterJava_temp_dir = path_to_SourceMeterJava_temp_dir
		if not os.path.exists(self.path_to_SourceMeterJava_temp_dir):
			os.makedirs(self.path_to_SourceMeterJava_temp_dir)
		os.environ["JAVA_HOME"] = os.path.dirname(os.path.dirname(self.path_to_Java_exe))
		os.environ["PATH"] = os.path.join(os.environ["JAVA_HOME"], "bin") + (";" if ";" in os.environ["PATH"] else ":") + os.environ["PATH"]

	def read_results(self, res_path):
		results = {"metrics": {}, "violations": {}}
		# Read metrics
		analysismetrics = set(["HCPL","HDIF","HEFF","HNDB","HPL","HPV","HTRP","HVOL","MIMS",\
							   "MI","MISEI","MISM","McCC","NL","NLE","NII","NOI","CD","CLOC",\
							   "DLOC","TCD","TCLOC","LOC","LLOC","NUMPAR","NOS","TLOC","TLLOC"])
		with open(res_path + "-Method.csv") as infile:
			metrics = [l[1:-1] for l in next(infile).strip().split(',')]
			values = [l for l in next(infile).strip().split('","')]
			values = [values[0][1:]] + values[1:-1] + [values[-1][:-1]]

			# Convert to numeric values
			for i, n in enumerate(values):
				try: values[i] = int(n)
				except:
					try: values[i] = float(n)
					except: pass
			for metric, value in zip(metrics[10:47], values[10:47]):
				if metric in analysismetrics:
					results["metrics"][metric] = value

			# Get violation stats
			metricsPMD = metrics[48:49] + metrics[50:52] + metrics[53:54] + metrics[55:56] + metrics[58:59] + metrics[61:65] + metrics[66:67] 
			valuesPMD = values[48:49] + values[50:52] + values[53:54] + values[55:56] + values[58:59] + values[61:65] + values[66:67] 
			results["violations"]["stats"] = {}
			for metric, value in zip(metricsPMD, valuesPMD):
				results["violations"]["stats"][metric] = value

			# Read violations
			results["violations"]["violations"] = {}
			with open(res_path + "-PMD.txt") as infile:
				for line in infile:
					line = line.strip().split("MyClass.java(")[-1].split(':')
					violationline, violationid = int(line[0][:-1]) - 4, line[1][1:] # -4 used to correct for line number
					if violationid in results["violations"]["violations"]:
						results["violations"]["violations"][violationid] = [results["violations"]["violations"][violationid]]
						results["violations"]["violations"][violationid].append(violationline)
					else:
						results["violations"]["violations"][violationid] = violationline

			if "PMD_UPM" in results["violations"]["violations"]:
				results["violations"]["stats"]["WarningMajor"] -= 1
				results["violations"]["stats"]["Best Practice Rules"] -= 1
				if type(results["violations"]["violations"]["PMD_UPM"]) is list:
					results["violations"]["violations"]["PMD_UPM"].pop(0)
				else:
					del results["violations"]["violations"]["PMD_UPM"]

			return results

	def run_analysis(self, project_path, read_results = True):
		project_name = project_path.split(os.path.sep)[-1]
		results_path = self.path_to_SourceMeterJava_temp_dir + os.path.sep + project_name + "Results"
		cmd = [self.path_to_SourceMeterJava_exe, "-projectName=" + project_name, "-projectBaseDir=" + project_path, "-resultsDir=" + results_path]
		log = ""
		proc = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT)
		for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
			log += line
			if line.strip() == "Done!":
				# Get latest analysis path
				res_path = results_path + os.path.sep + project_name + os.path.sep + "java"
				res_path += os.path.sep + sorted(os.listdir(res_path))[-1]
				res_path += os.path.sep + project_name
				if read_results:
					return self.read_results(res_path)
				else:
					return 0
		res_path = results_path + os.path.sep + project_name + os.path.sep + "java"
		res_path += os.path.sep + sorted(os.listdir(res_path))[-1]
		res_path += os.path.sep + project_name
		if read_results:
			return self.read_results(res_path)
		else:
			return 0
		print("Error in SourceMeterJava")
		print(log)
		return -1

	def analyze_method(self, method_code, read_results = True):
		project_path = os.path.join(self.path_to_SourceMeterJava_temp_dir, "MyProject")
		if not os.path.exists(os.path.join(project_path, "mypackage")):
			os.makedirs(os.path.join(project_path, "mypackage"))
		filename = os.path.join(project_path, "mypackage", "MyClass.java")
		with open(filename, 'w') as outfile:
			outfile.write("package mypackage;\n\n")
			outfile.write("class MyClass{\n\n")
			outfile.write(method_code + "\n")
			outfile.write("}\n")
		return self.run_analysis(project_path, read_results)

	def cleanup(self):
		project_path = os.path.join(self.path_to_SourceMeterJava_temp_dir, "MyProject")
		results_path = os.path.join(self.path_to_SourceMeterJava_temp_dir, "MyProjectResults")
		try:
			shutil.rmtree(project_path)
		except OSError:
			pass
		try:
			shutil.rmtree(results_path)
		except OSError:
			pass

if __name__ == '__main__':
	sm = MetricsAnalyzer(javaExePath, sourcemeterExePath, tempDirPath)

	results = sm.analyze_method(r"""	/**
	 * Render a default HTML "Whitelabel Error Page".
	 * <p>
	 * Useful when no other error view is available in the application.
	 * @param responseBody the error response being built
	 * @param error the error data as a map
	 * @return a Publisher of the {@link ServerResponse}
	 */
	protected Mono<ServerResponse> renderDefaultErrorView(
			ServerResponse.BodyBuilder responseBody, Map<String, Object> error) {
		StringBuilder builder = new StringBuilder();
		Date timestamp = (Date) error.get("timestamp");
		Object message = error.get("message");
		Object trace = error.get("trace");
		Object requestId = error.get("requestId");
		builder.append("<html><body><h1>Whitelabel Error Page</h1>").append(
				"<p>This application has no configured error view, so you are seeing this as a fallback.</p>")
				.append("<div id='created'>").append(timestamp).append("</div>")
				.append("<div>[").append(requestId)
				.append("] There was an unexpected error (type=")
				.append(htmlEscape(error.get("error"))).append(", status=")
				.append(htmlEscape(error.get("status"))).append(").</div>");
		if (message != null) {
			builder.append("<div>").append(htmlEscape(message)).append("</div>");
		}
		if (trace != null) {
			builder.append("<div style='white-space:pre-wrap;'>")
					.append(htmlEscape(trace)).append("</div>");
		}
		builder.append("</body></html>");
		return responseBody.syncBody(builder.toString());
	}""", False)

	print(json.dumps(results, indent=3))



