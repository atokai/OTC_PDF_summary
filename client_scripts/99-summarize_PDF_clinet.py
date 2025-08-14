import sys
import os
import time
import base64
import requests

# API Endpoints
SUBMIT_URL = os.environ.get("PDF_Submission_API_URL")
STATUS_URL = os.environ.get("PDF_Status_API_URL")
SUMMARY_URL = os.environ.get("PDF_Summary_API_URL")

def upload_pdf(file_path):
    """Uploads the PDF and returns a task_id"""
    print("\nUploading PDF...")
    if not os.path.exists(file_path):
        print(f" Error: File '{file_path}' not found.")
        sys.exit(1)
    with open(file_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "file_name": os.path.basename(file_path),
        "file_data": encoded_pdf
    }
    response = requests.post(SUBMIT_URL, json=payload, headers={"Content-Type": "application/json"})
    try:
        data = response.json()
        task_id = data.get("task_id")
        print(" Task ID:", task_id)
        return task_id
    except Exception as e:
        print(" Failed to parse response JSON:", str(e))
        sys.exit(1)

def poll_status(task_id, interval=15):
    """Polls the status endpoint every `interval` seconds until done"""
    print("\nPolling for status...")
    while True:
        params = {"task_id": task_id}
        response = requests.get(STATUS_URL, params=params)
        try:
            data = response.json()
            status = data.get("message", "unknown")
            print(f" Status: {status}")
            if status == "06-SummaryUploaded":
                break
        except Exception as e:
            print(" Error parsing status:", str(e))
        time.sleep(interval)

def fetch_summary(task_id):
    """Fetches and prints the final summary"""
    print("\nFetching summary...")
    params = {"task_id": task_id}
    response = requests.get(SUMMARY_URL, params=params)
    try:
        data = response.json()
        summary = data.get("message", "No summary found.")
        print("\n Summary:\n")
        print(summary)
    except Exception as e:
        print("Error parsing summary:", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 99-summarize_PDF_client.py <PDF_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    # Step 1: Upload PDF
    task_id = upload_pdf(file_path)
    # Step 2: Poll status until complete
    poll_status(task_id)
    # Step 3: Fetch the summary
    fetch_summary(task_id)
