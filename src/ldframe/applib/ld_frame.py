import json
from pyld import jsonld
from rdflib import ConjunctiveGraph
from ldframe.utils.logs import app_logger


class Frame(object):
    """Handle Linked Data Framing requests."""

    def __init__(self, ld_frame, source_data):
        """Init Object."""
        self.ld_frame = ld_frame
        self.source_data = source_data

    def _doc_type(self):
        """Parse JSON-LD frame and establish document type."""
        pass

    def _doc_id(self, graph_object):
        """Parse JSON-LD frame and establish document id."""
        pass

    def _merge_graphs(self):
        """Merge graphs received for framing."""
        pass

    def _create_ld(self):
        """Create JSON-LD output for the given subject."""
        graph = ConjunctiveGraph()
        graph.parse(data=self._merge_graphs, format="turtle")
        try:
            # pyld likes nquads, by default
            expanded = jsonld.from_rdf(graph.serialize(format="nquads"))
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
        header_line = {action: {"_type": self._doc_type(), "_id": self._doc_id()}}
        graphs = self._create_ld()
