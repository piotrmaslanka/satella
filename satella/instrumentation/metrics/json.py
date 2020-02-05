"""
Routines for manipulating the JSON emitted by the metrics
"""
import copy
import logging
from satella.coding import for_argument

logger = logging.getLogger(__name__)


@for_argument(copy.copy, copy.copy)
def are_equal(tree1, tree2) -> bool:
    tree1.pop('_', None)
    tree2.pop('_', None)
    tree1.pop('_timestamp', None)
    tree2.pop('_timestamp', None)
    return tree1 == tree2


def is_leaf_node(tree: dict) -> bool:
    for v in tree.values():
        if isinstance(v, (dict, list, tuple)):
            return False
    return True


def annotate_every_leaf_node_with_labels(tree, labels):
    """
    Add given labels to every leaf node in the tree.

    :param tree: tree to modify in-place
    :param labels: dictionary of labels to add
    :return: tree
    """
    if isinstance(tree, list):
        return [annotate_every_leaf_node_with_labels(q, labels) for q in tree]

    if is_leaf_node(tree):
        tree.update(labels)
        return tree

    for k in tree.keys():
        if k == '_timestamp':
            continue
        if not isinstance(tree[k], (list, dict)):
            continue
        tree[k] = annotate_every_leaf_node_with_labels(tree[k], labels)

    return tree


@for_argument(copy.copy, copy.copy)
def update(tree1, tree2):
    """
    Merge two dictionaries generated by Metric.to_json

    Values from tree2 take precendence

    :param tree1: a dictionary, generated by Metric.to_json
    :param tree2: a dictionary to update with, generated by Metric.to_json
    :return: a new dictionary, resulting from merging tree1 with tree2
    """

    if not isinstance(tree1, (dict, list)) and not isinstance(tree2, (dict, list)):
        return tree2

    assert type(tree1) == type(tree2), 'Cannot merge different types!'

    if isinstance(tree1, list) and isinstance(tree2, list):
        output_list = tree1
        for v_b in tree2:
            tree2.remove(v_b)
            for i, v_a in enumerate(output_list):
                if are_equal(v_b, v_a):
                    output_list[i] = v_b
                    break
                else:
                    output_list.append(v_b)
        output_list.extend(tree2)
        return output_list

    return_tree = {}
    for k, v in tree1.items():
        v_b = tree2.pop(k, None)
        if v_b is None:
            return_tree[k] = v
        else:
            return_tree[k] = update(v, v_b)
    for k, v in tree2.items():
        return_tree[k] = v

    return return_tree

