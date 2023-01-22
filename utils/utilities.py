import xml.etree.ElementTree as ET
import sys
import traceback

def ast_to_xml_tree(ast):
    """
    :param ast: Abstract Syntax Tree in XML format
    :returns the XML tree
    """

    tree = ast.encode("utf-8")

    try:
        xml_tree = ET.fromstring(tree)
        return xml_tree
    except:
        print("Could not parse the following AST:\n")
        print(ast + "\n")
        print("Exiting...\n")
        sys.exit(traceback.format_exc())