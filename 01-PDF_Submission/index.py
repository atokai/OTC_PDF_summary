# -*- coding:utf-8 -*-
import datetime
import random
import string
import os
import json
import base64
from obs import ObsClient

def generate_unique_task_id():
    """Generate a unique directory name: YYYYMMDDHHMM-XYZ"""
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")  # UTC time
    random_hash = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # 3-char hash
    return f"{timestamp}-{random_hash}"

def write_status(obs_client, bucket_name, task_id, status):
    """Write the status to OBS."""
    status_path = '/tmp/status'
    with open(status_path, 'w') as f:
        f.write(status)
    obs_client.putFile(bucket_name, f'{task_id}/status', status_path)

def handler (event, context):
    OBS_IN_name = 'atokai-pdf-summary-in'
    OBS_OUT_name = 'atokai-pdf-summary-out'
    obsClient = ObsClient(
        access_key_id = os.environ.get("OTC_access_key_id"),
        secret_access_key = os.environ.get("OTC_secret_access_key"),
        server='https://obs.eu-de.otc.t-systems.com/'  # Ensure this matches your OBS region endpoint
    )

    try:
        # Ensure 'body' exists
        if "body" not in event:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing request body"})
            }
        # Decode the base64-encoded body
        body_encoded = event.get("body", "")
        body_decoded = base64.b64decode(body_encoded).decode('utf-8')
        body = json.loads(body_decoded)  # API Gateway sends body as JSON
        file_name = body.get("file_name", "uploaded.pdf")
        file_data = body.get("file_data")
        if not file_data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing file_data"})
            }        
        # Decode base64 data
        file_bytes = base64.b64decode(file_data)
        # Generating task_id
        task_id= generate_unique_task_id()
        # Write initial status
        write_status(obsClient, OBS_OUT_name, task_id, '00-WorkflowStarting')
        # Generate structured path
        object_key = task_id + '/' + file_name
        # Upload to OBS
        pdf_temp = '/tmp/file.PDF'
        with open(pdf_temp, "wb") as f:
            f.write(file_bytes)
        resp = obsClient.putFile(OBS_IN_name, object_key, pdf_temp)
        if resp.status < 300:
            print(f'Successfully uploaded to: {object_key}')
            # Write status after upload
            write_status(obsClient, OBS_OUT_name, task_id, '01-FileUploaded')
        else:
            print(f'Failed to upload. Error: {resp.errorCode}, {resp.errorMessage}')  
            # Write error status
            write_status(obsClient, OBS_OUT_name, task_id, '99-UploadFailed')
        # Return the task_id in the response       
        return {
            "statusCode": 200,  # Ensure statusCode is included
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "task_id": task_id,
            }),
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,  # Ensure error responses also have statusCode
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }  