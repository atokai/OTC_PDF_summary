# -*- coding:utf-8 -*-
import json
import base64
import os
from obs import ObsClient

def handler (event, context):
    OBS_OUT_name = 'atokai-pdf-summary-out'
    query_params = event.get('queryStringParameters', {})
    # Extract the task_id from query parameters
    task_id = query_params.get('task_id')
    print(f"Task ID from query parameters: {task_id}")
    if not task_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing query parameter 'task_id'."})
        }
    summary_object = f"{task_id}/summary.txt"
    OTC_access_key_id = os.environ.get("OTC_access_key_id")
    OTC_secret_access_key = os.environ.get("OTC_secret_access_key")
    obsClient = ObsClient(
        access_key_id = os.environ.get("OTC_access_key_id"),
        secret_access_key = os.environ.get("OTC_secret_access_key"),
        server='https://obs.eu-de.otc.t-systems.com/'  # Ensure this matches your OBS region endpoint
    )
    summary_temp = '/tmp/summary.txt'
    # Download the status object
    resp = obsClient.getObject(OBS_OUT_name, summary_object, summary_temp)
    if resp.status < 300:
        print(f'Successfully downloaded: {summary_object}')
    else:
        print(f'Failed to download. Error: {resp.errorCode}, {resp.errorMessage}')

    with open(summary_temp, "r") as f:
        summary = f.read()

    # Return the summary content
    return {
        "statusCode": 200,
        "isBase64Encoded": False,
         "body": json.dumps({
                "message": summary,
            }),
        "headers": {
            "Content-Type": "application/json"
        }
    }
     

