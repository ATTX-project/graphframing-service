import json
import requests
from ldframe.utils.logs import app_logger
# from datetime import datetime
# from ldframe.utils.broker import broker
# from ldframe.applib.messaging_publish import Publisher
from urlparse import urlparse
from requests_file import FileAdapter

artifact_id = 'GraphFraming'  # Define the IndexingService agent
agent_role = 'LDframe'  # Define Agent type


def handle_file_adapter(request, input_data):
    """Handle file adapter response."""
    if request.status_code == 404:
        raise IOError("Something went wrong with retrieving the file: {0}. It does not exist!".format(input_data))
    elif request.status_code == 403:
        raise IOError("Something went wrong with retrieving the file: {0}. Accessing it is not permitted!".format(input_data))
    elif request.status_code == 400:
        raise IOError("Something went wrong with retrieving the file: {0}. General IOError!".format(input_data))
    elif request.status_code == 200:
        return request.text


def retrieve_data(input_type, input_data):
    """Retrieve data from a specific URI."""
    s = requests.Session()
    allowed = ('http', 'https', 'ftp')
    local = 'file'
    if input_type == "Data":
        return input_data
    elif input_type == "URI":
        try:
            if urlparse(input_data).scheme in allowed:
                request = s.get(input_data, timeout=1)
                return request.text
            elif urlparse(input_data).scheme in local:
                s.mount('file://', FileAdapter())
                request = s.get(input_data)
                return handle_file_adapter(request, input_data)
        except Exception as error:
            app_logger.error('Something is wrong: {0}'.format(error))
            raise


def prov_message(message_data, status, start_time, end_time, replace_index):
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
    prov_msg["activity"]["title"] = "Indexing Service Operations."
    prov_msg["activity"]["status"] = status
    prov_msg["activity"]["startTime"] = start_time
    prov_msg["activity"]["endTime"] = end_time
    message["provenance"]["input"] = []
    message["provenance"]["output"] = []
    message["payload"] = {}
    if type(replace_index) is list:
        for index in replace_index:
            output_data = {
                "index": index,
                "key": "outputIndex",
                "role": "Dataset"
            }
            message["provenance"]["output"].append(output_data)
    else:
        output_data = {
            "index": replace_index,
            "key": "outputIndex",
            "role": "Dataset"
        }
        message["provenance"]["output"].append(output_data)

    alias_list = [str(r) for r in message_data["payload"]["indexingServiceInput"]["targetAlias"]]
    source_data = message_data["payload"]["indexingServiceInput"]["sourceData"]

    for elem in source_data:
        key = "index_{0}".format(source_data.index(elem))
        input_data = {
            "aliases": alias_list,
            "key": key,
            "role": "alias"
        }
        if elem["inputType"] == "Data":
            message["payload"][key] = "attx:tempDataset"
        if elem["inputType"] == "URI":
            message["payload"][key] = elem["input"]
        message["provenance"]["input"].append(input_data)
    message["payload"]["aliases"] = message_data["payload"]["indexingServiceInput"]["targetAlias"]
    message["payload"]["outputIndex"] = replace_index

    app_logger.info('Construct provenance metadata for Indexing Service.')
    return json.dumps(message)


def response_message(provenance_data, output):
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
    message["payload"]["indexingServiceOutput"] = output
    return message
