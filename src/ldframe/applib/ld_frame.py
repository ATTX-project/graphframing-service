import json
from pyld import jsonld
from rdflib import ConjunctiveGraph
from ldframe.utils.logs import app_logger
from os import environ
from ldframe.utils.convert import pyld_jsonld_from_rdflib_graph

gm = {'host': environ['GMHOST'] if 'GMHOST' in environ else "localhost",
      'api': environ['GMVER'] if 'GMVER' in environ else "0.2",
      'port': environ['GMPORT'] if 'GMPORT' in environ else 4302}


class Frame(object):
    """Handle Linked Data Framing requests."""

    def __init__(self, ld_frame, source_data, doc_type=None):
        """Init Object."""
        self.ld_frame = ld_frame
        self.source_data = source_data
        self.doc_type = doc_type

    def _doc_type(self):
        """Parse JSON-LD frame and establish document type."""
        if not self.doc_type:
            return json.loads(self.ld_frame)["@type"]
        else:
            return self.doc_type

    def _merge_graphs(self):
        """Merge graphs received for framing."""
        graph = ConjunctiveGraph()
        try:
            for key, unit in enumerate(self.source_data):
                if "contentType" in unit:
                    content_type = unit["contentType"]
                else:
                    content_type = "turtle"
                if "inputType" in unit and unit["inputType"] == "Graph":
                    request_url = 'http://{0}:{1}/{2}/graph?uri={3}'.format(gm['host'], gm['port'], gm['api'], unit["input"])
                    graph.parse(request_url, format=content_type)
                elif unit["inputType"] == "URI":
                    graph.parse(unit["input"], format=content_type)
                elif unit["inputType"] == "Data":
                    graph.parse(data=unit["input"], format=content_type)
                else:
                    raise IOError("Cannot read input source data.")
        except Exception as error:
            app_logger.error('Merging graphs failed with: {0}'.format(error))
            raise
        finally:
            return graph

    def _create_ld(self):
        """Create JSON-LD output for the given subject."""
        graph = self._merge_graphs().serialize(format="nquads")
        try:
            # pyld likes nquads, by default
            expanded = pyld_jsonld_from_rdflib_graph(graph)
            framed = jsonld.frame(expanded, json.loads(self.ld_frame))
            result = json.dumps(framed, indent=1, sort_keys=True)
            app_logger.info('Serialized as JSON-LD compact with the frame.')
        except Exception as error:
            app_logger.error('JSON-LD frame failed with error: {0}'.format(error))
            raise
        finally:
            return result

    def _bulk_data(self, action="index"):
        """Parse JSON-LD frame and establish document type."""
        graphs = json.loads(self._create_ld())
        text_file = []
        for key, graph_doc in enumerate(graphs["@graph"]):
            header_line = dict()
            header_line[action] = dict()
            header_line[action]["_type"] = self._doc_type()
            header_line[action]["_id"] = graph_doc["@id"]
            text_file.append(json.dumps(header_line))
            text_file.append(json.dumps(graph_doc))
        return "\n".join(text_file)
