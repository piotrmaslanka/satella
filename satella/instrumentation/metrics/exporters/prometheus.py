import logging
import io
import copy
from satella.coding import for_argument


from ..json import is_leaf_node

logger = logging.getLogger(__name__)


class RendererObject(io.StringIO):

    @for_argument(None, copy.copy)
    def render_node(self, tree, prefixes):
        if isinstance(tree, list):
            for elem in tree:
                self.render_node(elem, prefixes=prefixes)
            return

        if is_leaf_node(tree):
            self.write('_'.join(prefixes))
            curly_braces_used = len(tree) > 1
            if curly_braces_used:
                self.write('{')
            main_value = tree.pop('_')
            if curly_braces_used:
                labels = []
                for key, value in tree.items():
                    value = repr(value).replace('\\', '\\\\').replace('"', '\"').replace("'", '"')
                    labels.append('%s=%s' % (key, value))
                self.write(', '.join(labels))
                self.write('}')
            self.write(' %s\n' % (repr(main_value), ))

        else:
            for k, v in tree.items():
                if k == '_' and isinstance(v, list):
                    for elem in v:
                        self.render_node(elem, prefixes=prefixes)
                self.render_node(v, prefixes=prefixes + [k])


def json_to_prometheus(tree) -> str:
    """
    Render the JSON in the form understandable by Prometheus

    :param tree: JSON returned by the root metric (or any metric for that instance).
    :return: a string output to present to Prometheus
    """
    obj = RendererObject()
    obj.render_node(tree, [])
    return obj.getvalue()
