from .astextractor import ASTExtractor

class ASTAnalyzer(object):
	"""
	Class used as a python binding to the astextractor class
	used for calculating the AST of a given code
	"""
	def __init__(self, path_to_ASTExtractor, path_to_ASTExtractor_properties):
		"""
		Initializes this extractor.
		
		:param path_to_Java_exe: the path to the Java executable.
		:param path_to_RSM_jar: the path to the rsm.jar executable java archive.
		:param path_to_RSM_temp_dir: the path to the RSM temp directory for files/results.
		"""
		self.ast_extractor = ASTExtractor(path_to_ASTExtractor, path_to_ASTExtractor_properties)

	def code_to_ast(self, code):
		"""
		Extracts the Abstract Syntax Tree (AST) from the given source code.

		:param ast_extractor: an instance of the ast_extractor tool.
		:param code: the code of which the AST is extracted in string format.
		:returns: the Abstract Syntax Tree in string format.
		"""
		try:
			ast = self.ast_extractor.parse_string(code)
			final_ast = ast.splitlines()
			for block in reversed([l for l, line in enumerate(final_ast[1:]) if len(line) - len(line.lstrip(' ')) == 0 and line.startswith("</") and not line.startswith("</CompilationUnit")]):
				# closing at final_ast[block+1]
				opening = None
				for i in range(block + 1, 0, -1):
					if final_ast[i].lstrip().startswith("<" + final_ast[block+1].split("</")[1].split(">")[0] + ">"):
						opening = i
						break
				if opening:
					final_ast[opening:block + 2] = ["".join(n.rstrip() for n in final_ast[opening:block + 2])]
			myast = "\n".join(final_ast)
			myast = ast
			if not ast.lstrip().startswith("<CompilationUnit>"):
				ast = self.ast_extractor.parse_string("class SampleClass{\n" + code + "\n}\n")
				myast = "\n".join(ast.split("\n")[3:-3])
				if not myast.lstrip().startswith("<MethodDeclaration>"):
					ast = self.ast_extractor.parse_string("class SampleClass{\nvoid SampleMethod(){\n" + code + "\n}\n\n}\n")
					ast = "\n".join(ast.split("\n")[6:-4])
					myast = ast
			return myast
		except:
			print("Could not parse the following code:\n")
			print(code + "\n")
			print("Exiting...\n")
