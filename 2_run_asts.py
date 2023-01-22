import os
import json
import codecs
import csv
import xml.etree.ElementTree as ET
from libs.asts import ASTAnalyzer
from properties import datasetPath, resultsPath, pathToASTExtractor, pathToASTExtractorProperties

aa = ASTAnalyzer(pathToASTExtractor, pathToASTExtractorProperties)

if not os.path.exists(resultsPath):
	os.makedirs(resultsPath)

errors = 0
# Iterate over all snippets in dataset
for directory in ["train", "valid", "test"]:
	for jsonlfile in os.listdir(os.path.join(datasetPath, directory)):
		snippetsPath = os.path.join(datasetPath, directory, jsonlfile)
		with codecs.open(snippetsPath, encoding='utf-8', errors='ignore') as infile:
			total = len(list(enumerate(infile)))
		if not os.path.exists(os.path.join(resultsPath, jsonlfile.split(".")[0] + ".csv")):
			with open(os.path.join(resultsPath, jsonlfile.split(".")[0] + "_ast.csv"), 'w') as outfile:
				writer = csv.writer(outfile)
				writer.writerow(["url", "code", "doc", "ast", "ast_code", "ast_doc"])
				with codecs.open(snippetsPath, encoding='utf-8', errors='ignore') as infile:
					for i, line in enumerate(infile):
						print(str(i) + "/" + str(total))
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

						ast = aa.code_to_ast(documentation + code)
						ast_code = aa.code_to_ast(code)
						ast_doc = aa.code_to_ast(documentation)
						if (ast):
							try:
								tree = ast.encode("utf-8")
								xml_tree = ET.fromstring(tree)
								final_xml = ET.tostring(xml_tree, encoding='unicode')
								tree = ast_code.encode("utf-8")
								xml_tree = ET.fromstring(tree)
								final_xml_code = ET.tostring(xml_tree, encoding='unicode')
								tree = ast_doc.encode("utf-8")
								xml_tree = ET.fromstring(tree)
								final_xml_doc = ET.tostring(xml_tree, encoding='unicode')
								writer.writerow([snippetjson["url"], code, documentation, final_xml, final_xml_code, final_xml_doc])
							except:
								try:
									writer.writerow([snippetjson["url"], code, documentation, "-", "-", "-"])
								except UnicodeEncodeError: # this exception used only to catch unicode errors in filenames (very rare case)
									pass
						else:
							try:
								writer.writerow([snippetjson["url"], code, documentation, "-", "-", "-"])
							except UnicodeEncodeError: # this exception used only to catch unicode errors in filenames (very rare case)
								pass
							errors += 1
print("Total errors: " + str(errors))
