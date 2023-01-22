from nltk.tokenize import word_tokenize
from .utilities import ast_to_xml_tree


def cyclomatic_complexity(source_code):
    """
    Calculate the McCabe Cyclomatic Complexity for Java snippet manually without a flow control graph

    :param source_code
    :return: cc
    """
    cc = 1

    control_flow_statements = ["if", "else", "else if", "while", "for", "and"]

    tokens = word_tokenize(source_code)

    for w in control_flow_statements:
        cc = cc + tokens.count(w)

    return cc


def number_of_names(ast):
    """
    Calculate the number of variables,methods and objects of a snippet

    :param ast
    :return:
    """

    try:
        xml_tree = ast_to_xml_tree(ast)
        counter = 0

        for n in xml_tree.iter("SimpleName"):
            counter += 1

        return counter
    except:
        return -1
