from utils.tree import Node


def ast_tree_to_node_tree(ast_tree):
    """
    Transform the Abstract Syntax Tree to a Node tree

    :param ast_tree
    :return:
    """
    current_node = Node(str(ast_tree.tag))

    # # keep variables names
    # text = ast_tree.text
    #
    # if len(text.strip()) > 0:
    #     current_node.addkid(Node(text))

    for child in ast_tree:
        current_node.addkid(ast_tree_to_node_tree(child))

    return current_node
