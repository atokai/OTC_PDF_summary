import requests
import sys
import os

#API URL for the status requests
API_URL = os.environ.get("PDF_Status_API_URL")

def check_status(api_url, task_id):
    """Checks the status of a PDF processing task by task_id."""
    # Construct query string parameters
    params = {
        "task_id": task_id
    }
    # Send GET request with query parameters
    response = requests.get(api_url, params=params)
    # Debugging: Print the raw response
    print("\nResponse Status Code:", response.status_code)
    print("\nRaw Response Text:", response.text)  # This will show if it's empty or an error

if __name__ == "__main__":
    # Check if the task_id is provided
    if len(sys.argv) < 2:
        print("Error: missing attribute 'task_id'.")
        print("Usage: python 03-check_PDF_status.py <task_id>")
        sys.exit(1)
    task_id = sys.argv[1]
    # Call the check_status function
    check_status(API_URL, task_id)
