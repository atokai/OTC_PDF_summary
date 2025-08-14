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
    
    status_object = f"{task_id}/status"
    OTC_access_key_id = os.environ.get("OTC_access_key_id")
    OTC_secret_access_key = os.environ.get("OTC_secret_access_key")
    obsClient = ObsClient(
        access_key_id = os.environ.get("OTC_access_key_id"),
        secret_access_key = os.environ.get("OTC_secret_access_key"),
        server='https://obs.eu-de.otc.t-systems.com/'  # Ensure this matches your OBS region endpoint
    )
    # Check if the status object exists in OBS
    response = obsClient.getObjectMetadata(OBS_OUT_name, status_object)
    if response.status < 300:
        print(" status exists.")
        status_temp = '/tmp/status'
        # Download the status object
        resp = obsClient.getObject(OBS_OUT_name, status_object, status_temp)
        if resp.status < 300:
            print(f'Successfully downloaded: {status_object}')
        else:
            print(f'Failed to download. Error: {resp.errorCode}, {resp.errorMessage}')

        with open(status_temp, "r") as f:
            status_content = f.read()
        print(f"Status content: {status_content}")
        # Return the status content
        return {
            "statusCode": 200,
            "isBase64Encoded": False,
            "body": json.dumps({
                "message": status_content
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    else:
        print(f" status does not exist or error occurred: {response.status}, {response.errorMessage}")
        return {
            "statusCode": 404,
            "isBase64Encoded": False,
            "body": json.dumps({
                "message": "Status not found for the provided task_id."
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }