import json
from ldframe.utils.logs import app_logger
from datetime import datetime
from ldframe.utils.broker import broker
from ldframe.applib.messaging_publish import Publisher
from ldframe.applib.ld_frame import Frame
from ldframe.utils.file import results_path

artifact_id = 'GraphFraming'  # Define the IndexingService agent
agent_role = 'LDframe'  # Define Agent type


def ld_message(message_data):
    """Replace an old index with a new index for a given alias list."""
    startTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    ld_frame = message_data["payload"]["framingServiceInput"]["ldFrame"]
    doc_type = message_data["payload"]["framingServiceInput"]["docType"]
    source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
    PUBLISHER = Publisher(broker['host'], broker['user'], broker['pass'], broker['provqueue'])
    frame = Frame(ld_frame, source_data, doc_type)
    try:
        output_data = frame._bulk_data()
        output_uri = results_path(output_data, "json")
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "success", startTime, endTime, output_uri))
        app_logger.info('Generated an JSON-LD frame output at: .')
        return json.dumps(response_message(message_data["provenance"], output_uri), indent=4, separators=(',', ': '))
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "error", startTime, endTime, output_uri))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise


def prov_message(message_data, status, start_time, end_time, output_uri):
    """Construct GM related provenance message."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activity_id = message_data["provenance"]["context"]["activityID"]
    workflow_id = message_data["provenance"]["context"]["workflowID"]

    prov_msg = message["provenance"]

    prov_msg["context"] = dict()
    prov_msg["context"]["activityID"] = str(activity_id)
    prov_msg["context"]["workflowID"] = str(workflow_id)
    if message_data["provenance"]["context"].get('stepID'):
        prov_msg["context"]["stepID"] = message_data["provenance"]["context"]["stepID"]

    prov_msg["activity"] = dict()
    prov_msg["activity"]["type"] = "ServiceExecution"
    prov_msg["activity"]["title"] = "Graph Framing Service Operations."
    prov_msg["activity"]["status"] = status
    prov_msg["activity"]["startTime"] = start_time
    prov_msg["activity"]["endTime"] = end_time
    message["provenance"]["input"] = []
    message["provenance"]["output"] = dict()
    message["payload"] = {}
    output_data = {
        "key": "outputIndex",
        "role": "Dataset",
        "URI": output_uri
    }
    message["provenance"]["output"] = output_data
    source_data = message_data["payload"]["framingServiceInput"]["sourceData"]
    for graph in source_data:
        input_data = {
            "key": "inputGraphs_{0}".format(source_data.index(graph)),
            "role": "dataset",
        }
        key = "inputGraphs_{0}".format(source_data.index(graph))
        if graph["inputType"] == "Data":
            message["payload"][key] = "attx:tempDataset"
        if graph["inputType"] == "URI" or graph["inputType"] == "Graph":
            message["payload"][key] = graph["input"]
        message["provenance"]["input"].append(input_data)

    app_logger.info('Construct provenance metadata for Graph Framing Service.')
    return json.dumps(message)


def response_message(provenance_data, output_uri):
    """Construct Graph Manager response."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activity_id = provenance_data["context"]["activityID"]
    workflow_id = provenance_data["context"]["workflowID"]

    context_message = message["provenance"]

    context_message["context"] = dict()
    context_message["context"]["activityID"] = str(activity_id)
    context_message["context"]["workflowID"] = str(workflow_id)
    if provenance_data["context"].get('stepID'):
        context_message["context"]["stepID"] = provenance_data["context"]["stepID"]
    message["payload"] = dict()
    message["payload"]["indexingServiceOutput"] = output_uri
    return message
