import sys
import requests
import os
import base64

#API URL for the PDF submission
API_URL = os.environ.get("PDF_Submission_API_URL")

def upload_pdf(api_url, file_path):
    """Uploads a PDF file to the API Gateway"""
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return
    # Read file and encode as Base64
    with open(file_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
    # Construct request payload
    payload = {
        "file_name": os.path.basename(file_path),  # Extract filename
        "file_data": encoded_pdf
    }
    # Send POST request
    response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
    # Debugging: Print the raw response
    print("\nResponse Status Code:", response.status_code)
    print("\nRaw Response Text:", response.text)  # This will show if it's empty or an error
    # Try to parse JSON safely
    try:
        response_json = response.json()
        print("\nResponse JSON:", response_json)
    except requests.exceptions.JSONDecodeError:
        print("\nError: Response is not JSON. Check the API logs.")
    
if __name__ == "__main__":
    # Check if the PDF file is provided
    if len(sys.argv) < 2:
        print("Error: missing attribute 'PDF_file'.")
        print("Usage: python check_pdf-summariser.py <PDF_file>")
        sys.exit(1)
    PDF_file = sys.argv[1]
    # Call the upload function
    upload_pdf(API_URL, PDF_file)