# -*- coding:utf-8 -*-
import os
import json
import requests
from obs import ObsClient
from PyPDF2 import PdfReader
import openai

def write_status(obs_client, bucket_name, task_id, status):
    """Write the status to OBS."""
    status_path = '/tmp/status'
    with open(status_path, 'w') as f:
        f.write(status)
    obs_client.putFile(bucket_name, f'{task_id}/status', status_path)

def handler (event, context):
    tmp_object_path = event['Records'][0]['s3']['object']['key']
    task_id, file_name = tmp_object_path.split("%2F", 1)
    object_path = task_id + "/" + file_name
    OBS_IN_name = 'atokai-pdf-summary-in'
    OBS_OUT_name = 'atokai-pdf-summary-out'
    OTC_access_key_id = os.environ.get("OTC_access_key_id")
    OTC_secret_access_key = os.environ.get("OTC_secret_access_key")
    obsClient = ObsClient(
        access_key_id = os.environ.get("OTC_access_key_id"),
        secret_access_key = os.environ.get("OTC_secret_access_key"),
        server='https://obs.eu-de.otc.t-systems.com/'  # Ensure this matches your OBS region endpoint
    )
    # Write initial status
    write_status(obsClient, OBS_OUT_name, task_id, '02-SummaryGenerationStarted')

    try:
        pdf_temp = '/tmp/file.PDF'
        # Download the PDF from OBS
        resp = obsClient.getObject(OBS_IN_name, object_path, pdf_temp)
        if resp.status < 300:
            print(f'Successfully downloaded: {object_path}')
            # Write status after download
            write_status(obsClient, OBS_OUT_name, task_id, '03-PDFDownloaded')
        else:
            print(f'Failed to download. Error: {resp.errorCode}, {resp.errorMessage}')
            # Write error status
            write_status(obsClient, OBS_OUT_name, task_id, '99-DownloadFailed')
        # Extract PDF
        reader = PdfReader(pdf_temp)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        # Write status after text extraction
        write_status(obsClient, OBS_OUT_name, task_id, '04-TextExtracted')
        # Set up the client with your API key and base URL
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL")
            )
        # Send a request to the LLM
        # Write status before calling LLM
        write_status(obsClient, OBS_OUT_name, task_id, '05-LLMCallStarted')
        print(f' Calling LLM started...')
        chat_response = client.chat.completions.create(
            #model="Llama-3.3-70B-Instruct",
            #model="DeepSeek-Coder-V2-Lite-Instruct",
            #model="Qwen3-30B-A3B-FP8",
            model="Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes documents. Your summaries must include the document title, relevant page or sentence numbers, and a concise summary."},
                {"role": "user", "content": "Please summarize the following text:\n\n[Document excerpt here]"},
                {"role": "assistant", "content": """Title: OTC Catalog
                Pages: 1-3
                Summary: This document is a catalog of OTC products and services, providing detailed information on various offerings."""},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=30000
            )
        summary = chat_response.choices[0].message.content
        print(f' LLM call finished.')
        # Save summary to OBS
        summary_temp = '/tmp/file.txt'
        with open(summary_temp, "w") as f:
            f.write(summary)
        object_key = task_id + "/" + 'summary.txt'
        resp = obsClient.putFile(OBS_OUT_name, object_key, summary_temp)
        if resp.status < 300:
            print(f'Successfully uploaded to: {object_key}')
            # Write status after upload
            write_status(obsClient, OBS_OUT_name, task_id, '06-SummaryUploaded')
        else:
            print(f'Failed to upload. Error: {resp.errorCode}, {resp.errorMessage}')
            # Write error status
            write_status(obsClient, OBS_OUT_name, task_id, '99-SummaryUploadFailed')
        return {
            "statusCode": 200,  # Ensure statusCode is included
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Summary written" })
        }

    except Exception as e:
        print(" Error:", str(e))
        return {
            "statusCode": 500,  # Ensure error responses also have statusCode
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }   

