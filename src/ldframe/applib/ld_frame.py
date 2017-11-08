import json
from pyld import jsonld
from rdflib import ConjunctiveGraph
from ldframe.utils.logs import app_logger


def create_jsonLD(graph_data, filter_frame):
    """Create JSON-LD output for the given subject."""
    graph = ConjunctiveGraph()
    graph.parse(data=graph_data, format="turtle")
    try:
        # pyld likes nquads, by default
        expanded = jsonld.from_rdf(graph.serialize(format="nquads"))
        framed = jsonld.frame(expanded, json.loads(filter_frame))
        result = json.dumps(framed, indent=1, sort_keys=True)
        app_logger.info('Serialized as JSON-LD compact with the frame.')
        return result
    except Exception as error:
        app_logger.error('JSON-LD frame failed with error: {0}'.format(error))
        return error
